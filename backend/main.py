from functools import wraps
import logging
from pydantic import BaseModel
from llm_compliance_checker import check_dynamic as llm_check_dynamic, check_specific as llm_check_specific
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional, List, Dict, Any
import os
from compliance_checker import classify_directory, dynamic_checklist, specific_checklist
from compliance_checker.github_fetcher import GitHubFetcher
from repo_analyzer import (
    analyze_comprehensive,
    analyze_specific,
    ComprehensiveAnalysis,
    SpecificAnalysis
)
from diagram_agent import get_architecture_diagram
from fastapi.responses import FileResponse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

anthropic_api_key = os.getenv("anthropic_api_key")
groq_api_key = os.getenv("groq_api_key")

app = FastAPI()

DIAGRAM_CACHE_DIR = Path("diagram_cache")
DIAGRAM_CACHE_DIR.mkdir(exist_ok=True)

VALID_CATEGORIES = ["frontend", "backend", "infrastructure", "shared", "docs"]
VALID_ANALYSIS_TYPES = ["readme", "dependencies",
                        "structure", "naming", "git_metadata"]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API_URL = "https://api.github.com"


# --- Models ---

class TreeNode(BaseModel):
    name: str
    path: str
    type: str
    sha: str
    size: Optional[int] = None
    url: str
    last_modified: Optional[str] = None
    children: Optional[List['TreeNode']] = None


class FileObject(BaseModel):
    branch: str
    url: str
    path: str


TreeNode.model_rebuild()


# --- Decorators ---

def log_endpoint(func):
    """Logs start, success, and failure of an endpoint."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"{func.__name__} - Request started")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} - Request completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} - Request failed: {str(e)}")
            raise
    return wrapper


# --- Helpers ---

def get_headers(token: Optional[str] = None) -> dict:
    """Builds GitHub API request headers, optionally including a bearer token."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def build_nested_structure(tree_data: List[Dict]) -> Dict[str, Any]:
    """Converts a flat GitHub tree list into a nested dict structure."""
    root = {}
    for item in tree_data:
        path_parts = item["path"].split("/")
        current = root
        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1:
                if item["type"] == "tree":
                    current.setdefault(part, {})
                else:
                    current[part] = None
            else:
                current = current.setdefault(part, {})
    return root


def validate_category(category: str) -> None:
    """Raises HTTP 400 if the given category is not in VALID_CATEGORIES."""
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}"
        )


def validate_analysis_types(analysis_types: List[str]) -> None:
    """Raises HTTP 400 if any analysis type is not in VALID_ANALYSIS_TYPES."""
    for analysis_type in analysis_types:
        if analysis_type not in VALID_ANALYSIS_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid analysis type: {analysis_type}. Must be one of: {VALID_ANALYSIS_TYPES}"
            )


async def get_latest_commit_date(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    path: str,
    token: str
) -> str:
    """Returns the date of the most recent commit touching the given path, or empty string on failure."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
    params = {"path": path, "per_page": 1}
    try:
        resp = await client.get(url, headers=get_headers(token), params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data[0]["commit"]["committer"]["date"]
    except Exception:
        pass
    return ""


async def get_branch_commit_sha(
    owner: str,
    repo: str,
    branch: str,
    token: Optional[str] = None
) -> str:
    """Resolves a branch name to its latest commit SHA."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/ref/heads/{branch}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers(token))
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Branch not found or GitHub API error: {response.text}"
            )
        return response.json()["object"]["sha"]


async def get_branch_sha(
    owner: str,
    repo: str,
    branch: str,
    token: Optional[str] = None
) -> str:
    """Resolves a branch name to the SHA of its root tree."""
    commit_sha = await get_branch_commit_sha(owner, repo, branch, token)
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/commits/{commit_sha}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers(token))
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Commit not found: {response.text}"
            )
        return response.json()["tree"]["sha"]


async def fetch_tree_recursive_full(
    owner: str,
    repo: str,
    sha: str,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """Fetches the full recursive tree for a given tree SHA from the GitHub API."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers(token))
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub API error: {response.text}"
            )
        return response.json()


def fetch_directory_contents(owner: str, repo: str, path: str, branch: str, token: Optional[str]) -> tuple:
    """Fetches directory contents using GitHubFetcher. Returns (files, directories, api_url)."""
    fetcher = GitHubFetcher(token)
    return fetcher.fetch_directory_contents(owner, repo, path, branch)


# --- Routes ---

@app.get("/api")
async def root():
    return {"message": "GitHub File Tree API"}


@app.get("/api/tree")
@log_endpoint
async def get_file_tree_frontend(
    owner: str = Query(...),
    repo: str = Query(...),
    branch: str = Query(default="main"),
    token: str = Query(...)
):
    """Returns a structured tree with last-modified dates for root-level directories."""
    try:
        tree_sha = await get_branch_sha(owner, repo, branch, token)
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=get_headers(token))
            tree_list = resp.json().get("tree", [])

            root_dir_paths = [
                item["path"]
                for item in tree_list
                if "/" not in item["path"] and item["type"] == "tree"
            ]
            all_paths = ["."] + root_dir_paths

            dates = await asyncio.gather(*[
                get_latest_commit_date(client, owner, repo, p, token)
                for p in all_paths
            ])
            last_modified_map: Dict[str, str] = dict(zip(all_paths, dates))

        root_nodes: List[TreeNode] = []
        root_card_contents: List[TreeNode] = []

        for item in tree_list:
            if "/" not in item["path"]:
                root_card_contents.append(TreeNode(
                    name=item["path"],
                    path=item["path"],
                    type=item["type"],
                    sha=item["sha"],
                    url=item["url"]
                ))

                if item["type"] == "tree":
                    children_nodes: List[TreeNode] = []

                    for c in tree_list:
                        parts = c["path"].split("/")
                        if len(parts) > 1 and parts[0] == item["path"] and len(parts) == 2:
                            nested_children: List[TreeNode] = []

                            if c["type"] == "tree":
                                for gc in tree_list:
                                    gc_parts = gc["path"].split("/")
                                    if (
                                        len(gc_parts) == 3
                                        and gc_parts[0] == item["path"]
                                        and gc_parts[1] == parts[1]
                                    ):
                                        nested_children.append(TreeNode(
                                            name=gc_parts[-1],
                                            path=gc["path"],
                                            type=gc["type"],
                                            sha=gc["sha"],
                                            url=gc["url"]
                                        ))

                            children_nodes.append(TreeNode(
                                name=parts[-1],
                                path=c["path"],
                                type=c["type"],
                                sha=c["sha"],
                                url=c["url"],
                                children=nested_children or None
                            ))

                    root_nodes.append(TreeNode(
                        name=item["path"],
                        path=item["path"],
                        type=item["type"],
                        sha=item["sha"],
                        url=item["url"],
                        last_modified=last_modified_map.get(item["path"], ""),
                        children=children_nodes[:10]
                    ))

        root_nodes.insert(0, TreeNode(
            name="Root",
            path=".",
            type="tree",
            sha=tree_sha,
            url=url,
            last_modified=last_modified_map.get(".", ""),
            children=root_card_contents
        ))

        return {"owner": owner, "repo": repo, "tree": root_nodes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree-compact")
@log_endpoint
async def get_file_tree_compact(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    token: Optional[str] = Query(
        None, description="GitHub Personal Access Token")
):
    """Returns a compact nested dict representation of the repository tree."""
    try:
        tree_sha = await get_branch_sha(owner, repo, branch, token)
        tree_data = await fetch_tree_recursive_full(owner, repo, tree_sha, token)
        nested_structure = build_nested_structure(tree_data.get("tree", []))
        return {"owner": owner, "repo": repo, "branch": branch, "tree": nested_structure}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/classify-directory")
@log_endpoint
async def classify_dir(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    token: Optional[str] = Query(
        None, description="GitHub Personal Access Token")
):
    """Classifies a repository directory into a category."""
    try:
        category = classify_directory(owner, repo, branch, path, token or "")
        return {"category": category, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-dynamic")
@log_endpoint
async def check_dynamic(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    token: Optional[str] = Query(
        None, description="GitHub Personal Access Token")
):
    """Runs a dynamic compliance checklist against a directory."""
    try:
        return dynamic_checklist(owner, repo, branch, path, token or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-specific")
@log_endpoint
async def check_specific(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    category: str = Query(..., description="Directory category"),
    tests: List[int] = Query(...,
                             description="List of test indices to run (1-based)"),
    token: Optional[str] = Query(
        None, description="GitHub Personal Access Token")
):
    """Runs selected compliance checks for a specific directory category."""
    try:
        validate_category(category)
        test_selection = {test_num: True for test_num in tests}
        return specific_checklist(owner, repo, branch, path, category, test_selection, token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-repo/comprehensive", response_model=dict)
@log_endpoint
async def api_analyze_repo_comprehensive(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    groq_api_key: Optional[str] = Query(None, description="Groq API key")
):
    """Runs a full LLM analysis covering README, dependencies, structure, naming, and git metadata."""
    try:
        result = analyze_comprehensive(
            owner, repo, branch, github_token, groq_api_key)
        if not result:
            raise HTTPException(
                status_code=404, detail="Failed to generate analysis.")
        return {
            "repository": f"{owner}/{repo}",
            "branch": branch,
            "analysis_type": "comprehensive",
            "result": result.model_dump() if isinstance(result, ComprehensiveAnalysis) else result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-repo/specific", response_model=dict)
@log_endpoint
async def api_analyze_repo_specific(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    analysis_types: List[str] = Query(...,
                                      description="Analysis types to run"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    groq_api_key: Optional[str] = Query(None, description="Groq API key")
):
    """Runs LLM analysis on selected aspects of a repository."""
    try:
        validate_analysis_types(analysis_types)
        result = analyze_specific(
            owner, repo, branch, analysis_types, github_token, groq_api_key)
        if not result:
            raise HTTPException(
                status_code=404, detail="Failed to generate analysis.")
        return {
            "repository": f"{owner}/{repo}",
            "branch": branch,
            "analysis_type": "specific",
            "analyzed_aspects": analysis_types,
            "result": result.model_dump() if isinstance(result, SpecificAnalysis) else result
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm-check-dynamic")
@log_endpoint
async def api_llm_check_dynamic(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    groq_api_key: Optional[str] = Query(None, description="Groq API key")
):
    """Runs an LLM-based compliance check with automatic directory classification."""
    try:
        files, directories, api_url = fetch_directory_contents(
            owner, repo, path, branch, github_token)
        return llm_check_dynamic(files, directories, path, api_url, groq_api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm-check-specific")
@log_endpoint
async def api_llm_check_specific(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    category: str = Query(..., description="Directory category"),
    tests: List[int] = Query(...,
                             description="List of test indices to run (1-based)"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    groq_api_key: Optional[str] = Query(None, description="Groq API key")
):
    """Runs an LLM-based compliance check for specific tests within a given category."""
    try:
        validate_category(category)
        files, directories, api_url = fetch_directory_contents(
            owner, repo, path, branch, github_token)
        test_selection = {test_num: True for test_num in tests}
        return llm_check_specific(files, directories, category, test_selection, api_url, groq_api_key)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-hybrid")
@log_endpoint
async def api_check_hybrid(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    path: str = Query(..., description="Directory path in the repository"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    groq_api_key: Optional[str] = Query(None, description="Groq API key")
):
    """
    Runs both deterministic and LLM-based checks and compares results.
    Each check is marked as passed, failed, or inconclusive based on agreement.
    """
    try:
        files, directories, api_url = fetch_directory_contents(
            owner, repo, path, branch, github_token)

        deterministic_result = dynamic_checklist(
            owner, repo, branch, path, github_token)
        llm_result = llm_check_dynamic(
            files, directories, path, api_url, groq_api_key)

        det_report = deterministic_result['report']
        llm_report = llm_result['report']

        if det_report['category'] != llm_report['category']:
            return {
                "report": {
                    "category": f"mismatch: {det_report['category']} vs {llm_report['category']}",
                    "url": api_url,
                    "total_checks": 0,
                    "passed": 0,
                    "failed": 0,
                    "inconclusive": 0,
                    "results": [{
                        "check": "category_classification",
                        "passed": "inconclusive",
                        "message": f"Deterministic: {det_report['category']}, LLM: {llm_report['category']}",
                        "severity": "error"
                    }]
                }
            }

        llm_checks = {r['check']: r for r in llm_report['results']}
        hybrid_results = []

        for det_check in det_report['results']:
            check_name = det_check['check']
            llm_check = llm_checks.get(check_name)

            if not llm_check:
                hybrid_results.append({
                    "check": check_name,
                    "passed": "inconclusive",
                    "message": f"Deterministic: {det_check['message']}. LLM: No result",
                    "severity": det_check['severity']
                })
                continue

            det_passed = det_check['passed']
            llm_passed = llm_check['passed']

            if det_passed == llm_passed:
                hybrid_results.append({
                    "check": check_name,
                    "passed": det_passed,
                    "message": det_check['message'] if det_passed else llm_check['message'],
                    "severity": det_check['severity']
                })
            else:
                hybrid_results.append({
                    "check": check_name,
                    "passed": "inconclusive",
                    "message": f"Deterministic: {det_check['message']}. LLM: {llm_check['message']}",
                    "severity": det_check['severity']
                })

        return {
            "report": {
                "category": det_report['category'],
                "url": api_url,
                "total_checks": len(hybrid_results),
                "passed": sum(1 for r in hybrid_results if r['passed'] is True),
                "failed": sum(1 for r in hybrid_results if r['passed'] is False),
                "inconclusive": sum(1 for r in hybrid_results if r['passed'] == "inconclusive"),
                "results": hybrid_results
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/diagram/architecture_diagram")
@log_endpoint
async def generate_architecture_diagram(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    refresh: bool = Query(default=False, description="Force a new generation"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token"),
    llm_api_key: Optional[str] = Query(
        None, description="LLM API key")
):
    """Returns a cached architecture diagram PNG, generating a new one on cache miss or forced refresh."""
    cache_filename = f"{owner}_{repo}_{branch}_architecture.png".replace(
        "/", "_")
    cache_path = DIAGRAM_CACHE_DIR / cache_filename

    if cache_path.exists() and not refresh:
        logger.info(
            f"Cache hit: returning existing diagram for {owner}/{repo}")
        return FileResponse(path=str(cache_path), media_type="image/png", filename=cache_filename)

    logger.info(
        f"{'Forced refresh' if refresh else 'Cache miss'}: generating diagram for {owner}/{repo}")
    try:
        result_path = await get_architecture_diagram(
            owner, repo, branch, cache_path, github_token, llm_api_key
        )
        return FileResponse(path=str(result_path), media_type="image/png", filename=cache_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/repo/file-summary")
@log_endpoint
async def get_repo_file_summary(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(default="main", description="Branch name"),
    github_token: Optional[str] = Query(
        None, description="GitHub Personal Access Token")
):
    """Returns a count of files grouped by extension for the given repository."""
    token = github_token or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404, detail="Repository or branch not found.")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code,
                            detail="GitHub API error.")

    extension_counts: dict[str, int] = {}
    total_files = 0

    for item in response.json().get("tree", []):
        if item["type"] != "blob":
            continue
        total_files += 1
        name = item["path"].split("/")[-1]
        ext = ("." + name.rsplit(".", 1)[-1]
               ) if "." in name else "(no extension)"
        extension_counts[ext] = extension_counts.get(ext, 0) + 1

    return {
        "repo": {"owner": owner, "name": repo, "branch": branch},
        "total_files": total_files,
        "file_summary": dict(sorted(extension_counts.items(), key=lambda x: x[1], reverse=True))
    }


@app.get("/api/repo/commit-history")
@log_endpoint
async def get_latest_commit_time(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    branch: str = Query(..., description="Branch name"),
    token: str = Query(..., description="GitHub Personal Access Token")
) -> str:
    """Returns the date of the most recent commit on the given branch."""
    commit_sha = await get_branch_commit_sha(owner, repo, branch, token)
    if not commit_sha:
        return "no sha"
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits?sha={commit_sha}&per_page=1"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=get_headers(token))
        if resp.status_code == 200:
            data = resp.json()
            return data[0]["commit"]["committer"]["date"] if data else "no data"
    return "couldn't sync with github"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
