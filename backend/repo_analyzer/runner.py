# runner.py
"""
Main runner for repository analysis.
"""

from typing import Dict, Any, Optional
from .readme_analyzer import analyze_readme as _analyze_readme
from .dependency_analyzer import analyze_dependencies as _analyze_dependencies
from .structure_analyzer import analyze_structure as _analyze_structure
from .naming_analyzer import analyze_naming_conventions as _analyze_naming
from .git_metadata_analyzer import analyze_git_metadata as _analyze_git


def analyze_readme(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find and extract README file from repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with README info or None if not found
    """
    return _analyze_readme(repo_owner, repo_name, branch, github_pat)


def analyze_dependencies(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find and extract dependency files from repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with dependency info or None if not found
    """
    return _analyze_dependencies(repo_owner, repo_name, branch, github_pat)


def analyze_structure(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze repository structure.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with structure analysis or None if failed
    """
    return _analyze_structure(repo_owner, repo_name, branch, github_pat)


def analyze_naming_conventions(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze naming conventions across repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with naming analysis or None if failed
    """
    return _analyze_naming(repo_owner, repo_name, branch, github_pat)


def analyze_git_metadata(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze git metadata (commits, branches, etc.).

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with git metadata analysis or None if failed
    """
    return _analyze_git(repo_owner, repo_name, branch, github_pat)


def analyze_repo_full(
    repo_owner: str,
    repo_name: str,
    branch: str = 'main',
    github_pat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run all analyzers and return combined report.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        branch: Branch name
        github_pat: GitHub personal access token (optional)

    Returns:
        Dict with all analysis results
    """
    return {
        'repository': {
            'owner': repo_owner,
            'name': repo_name,
            'branch': branch
        },
        'readme': analyze_readme(repo_owner, repo_name, branch, github_pat),
        'dependencies': analyze_dependencies(repo_owner, repo_name, branch, github_pat),
        'structure': analyze_structure(repo_owner, repo_name, branch, github_pat),
        'naming': analyze_naming_conventions(repo_owner, repo_name, branch, github_pat),
        'git_metadata': analyze_git_metadata(repo_owner, repo_name, branch, github_pat)
    }
