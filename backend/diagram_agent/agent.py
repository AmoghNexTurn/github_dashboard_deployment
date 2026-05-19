import asyncio
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

MAX_RETRIES = 3

LLM_REGISTRY: dict[str, BaseChatModel] = {
    "anthropic": ChatAnthropic(model_name="claude-haiku-4-5", temperature=0,
                               stop=["Observation:", "Thought:", "Action:"], timeout=120, api_key=SecretStr(os.environ.get("ANTHROPIC_API_KEY", ""))),
    "openai": ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        timeout=120,
        api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")),
    ),
    "novita": ChatOpenAI(
        model="moonshotai/kimi-k2.6",
        temperature=0,
        timeout=120,
        base_url="https://api.novita.ai/v3/openai",
        api_key=SecretStr(os.environ.get("NOVITA_API_KEY", "")),
    ),
}

ACTIVE_LLM = LLM_REGISTRY["anthropic"]  # Change this to switch LLMs


MERMAID_PROMPT_TEMPLATE = """Generate a mermaid flowchart diagram for the overall architecture of the {owner}/{repo} repository on the {branch} branch. Output only the mermaid code, no explanations. Follow the rules:

* Always use `graph TD` (top to bottom) — this significantly reduces edge crossings compared to left-to-right layouts
* Group components into subgraphs using only these layer IDs, ordered top to bottom as listed (include only layers that are present in the repo):
  - ClientLayer — end users (web browsers, mobile apps)
  - FrontendLayer — client-side applications (React, Vue, Next.js)
  - BackendLayer — main application server (Express, Django, FastAPI)
  - BusinessLogicLayer — internal services or domain modules
  - AuthLayer — authentication and authorization (JWT, OAuth, Passport)
  - DataLayer — primary databases (PostgreSQL, MongoDB, MySQL)
  - CacheLayer — caching and session storage (Redis, Memcached)
  - FileStorage — file and object storage (S3, local uploads, GCS)
  - ExternalServices — third-party APIs (Stripe, SendGrid, Twilio, OpenAI)
  - CloudInfra — cloud services, VMs, container orchestration (AWS, GCP, Kubernetes, Docker)
* Only include layers that are clearly present in the repo — skip any that do not apply
* Each node must represent a distinct architectural component — not a file, route, or function

* Node count and granularity rules (critical for a clean layout):
  - Aim for 2-4 nodes per subgraph — merge closely related components into a single node if needed
  - Do not represent individual API endpoints as nodes — they belong inside the server node conceptually
  - Do not represent individual service modules as separate nodes if they all serve the same purpose — group them into one node (e.g. "Analysis Services" instead of four separate service nodes)
  - Prefer breadth of 2 at most — if a node connects to more than 2 children in the same layer, consolidate those children into a single grouped node

* Edge rules (critical for a clean layout):
  - Only draw edges between adjacent or near-adjacent layers — avoid long-range cross-layer edges wherever possible
  - Every edge must pass through the correct intermediate layer — do not skip layers
  - Label each edge with the interaction type if it can be inferred (e.g. HTTP, REST API, Query/Insert, gRPC, pub/sub)
  - Maximum 1-2 outgoing edges per node — consolidate targets into a grouped node if more are needed
  - Do not duplicate relationships — one edge per node pair maximum

* Every node must be connected — no isolated or disconnected components
* Do not include implementation details like file names, route paths, or controller names
* Subgraph syntax must be exactly `subgraph ID` with no quoted label — never use `subgraph ID["Label"]`
  - Use only the exact layer IDs listed above
* Node label rules:
  - Use plain text only — no HTML tags like <br/> or <b>
  - Use a hyphen to separate descriptor text within a label (e.g. "Web Browser - Customer")

Format the output as a mermaid code block like this:
````mermaid
graph TD
    <nodes, edges, and optional subgraphs here>
````
Just respond with the mermaid code block, no additional text or explanation."""

DIAGRAMS_TRANSLATION_PROMPT = """You are given a Mermaid architecture diagram. Convert it into a valid, runnable Python script using the `diagrams` library (pip install diagrams).

Mermaid diagram:
{mermaid_code}

Rules for the output Python script:
- Import only from `diagrams`, `diagrams.onprem.*`, `diagrams.aws.*`, `diagrams.gcp.*`, `diagrams.azure.*`, `diagrams.generic.*`, `diagrams.saas.*`, `diagrams.programming.*`
- Map each mermaid subgraph to a `with Cluster("..."):` block with a human-readable label
- Map each mermaid node to the most semantically appropriate diagrams node class:
    * Web browsers / end users -> diagrams.onprem.client.Users
    * React / Vue / Next.js frontend -> diagrams.programming.framework.React (or Vue, Angular)
    * Express / Django / FastAPI server -> diagrams.onprem.compute.Server
    * PostgreSQL -> diagrams.onprem.database.PostgreSQL
    * MongoDB -> diagrams.onprem.database.MongoDB
    * MySQL -> diagrams.onprem.database.Mysql
    * Redis -> diagrams.onprem.inmemory.Redis
    * S3 / object storage -> diagrams.aws.storage.S3
    * JWT / Auth service -> diagrams.onprem.identity.Dex
    * Stripe -> diagrams.saas.payment.Stripe
    * SendGrid / email -> diagrams.saas.communication.Twilio (closest available)
    * OpenAI / external API -> diagrams.onprem.compute.Server with the label from the diagram
    * Kubernetes -> diagrams.onprem.container.K3S
    * Docker -> diagrams.onprem.container.Docker
    * Generic / unknown -> diagrams.generic.compute.Rack
- Node label rules (critical for readability):
    * Keep node labels to 1-3 words maximum — never paste the full mermaid node label in
    * Strip the layer prefix from labels (e.g. "FastAPI Server - REST API" -> "FastAPI Server")
    * Use the Cluster label to carry the descriptive context, not the node label
    * If two nodes in the same cluster would have the same short label, append a one-word qualifier
- Layout rules (critical — violations cause the diagram to collapse into a vertical stack):
    * Do NOT nest clusters more than one level deep — flatten any deeper nesting into sibling clusters
    * Do NOT put more than 3 nodes inside a single cluster — if a mermaid subgraph has more, split them into sibling clusters with descriptive names (e.g. "API Routes 1", "API Routes 2") or consolidate nodes into a single grouped node using a list: [Node("A"), Node("B")]
    * Represent grouped sibling nodes as a Python list on one line: `apis = [Server("Orders"), Server("Cart"), Server("Users")]` — this forces Graphviz to lay them out horizontally
    * Never stack independent nodes vertically inside a cluster when they could be expressed as a list
- Reproduce edges using >> with Edge(label="...") where the mermaid edge has a label; keep edge labels to 1-2 words
- Set graph_attr={{"rankdir": "LR", "splines": "ortho", "nodesep": "0.8", "ranksep": "1.2"}} on the Diagram to reinforce left-to-right layout at the Graphviz level
- Use `with Diagram("Architecture", filename="{output_stem}", show=False, direction="LR", graph_attr={{"rankdir": "LR", "splines": "ortho", "nodesep": "0.8", "ranksep": "1.2"}}):` as the outermost context
- Output ONLY a fenced python code block — no prose, no explanation

````python
# your script here
```"""


def extract_mermaid_code(response: str) -> str | None:
    match = re.search(r"```mermaid\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_python_code(response: str) -> str | None:
    match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def translate_mermaid_to_diagrams(
    mermaid_code: str,
    output_path: Path,
    llm: BaseChatModel,
) -> str:
    prompt = DIAGRAMS_TRANSLATION_PROMPT.format(
        mermaid_code=mermaid_code,
        output_stem=output_path.stem,
    )
    response = ACTIVE_LLM.invoke([{"role": "user", "content": prompt}])
    return str(response.content)


def generate_diagrams_diagram(
    mermaid_code: str,
    output_path: Path,
    llm: BaseChatModel,
) -> Path:
    for attempt in range(1, MAX_RETRIES + 1):
        raw_response = translate_mermaid_to_diagrams(
            mermaid_code, output_path, llm)
        script = extract_python_code(raw_response)

        if script is None:
            print(
                f"Translation attempt {attempt}/{MAX_RETRIES}: no python block found, retrying...")
            continue

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            dir=output_path.parent,
            delete=False,
        ) as tmp:
            tmp.write(script)
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run(
                [sys.executable, str(tmp_path)],
                capture_output=True,
                text=True,
                cwd=str(output_path.parent),
            )
        finally:
            tmp_path.unlink(missing_ok=True)

        if result.returncode != 0:
            print(
                f"Translation attempt {attempt}/{MAX_RETRIES}: script execution failed.\n"
                f"stderr: {result.stderr}\nRetrying..."
            )
            continue

        generated = output_path.parent / f"{output_path.stem}.png"
        if not generated.exists():
            print(
                f"Translation attempt {attempt}/{MAX_RETRIES}: output file not found, retrying...")
            continue

        if generated != output_path:
            generated.rename(output_path)

        return output_path

    raise RuntimeError(
        f"Failed to generate a diagrams diagram after {MAX_RETRIES} attempts."
    )


async def get_architecture_diagram(
    owner: str,
    repo: str,
    branch: str,
    output_path: Path,
    github_token: str | None = None,
    llm_api_key: str | None = None,
) -> Path:
    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {
                    "Authorization": f"Bearer {github_token or os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}"
                },
            }
        }
    )

    ALLOWED_TOOLS = {
        "get_file_contents",
        "list_branches",
        "list_commits",
        "search_code",
        "search_repositories",
    }

    def filter_tools(tools: list) -> list:
        return [t for t in tools if t.name in ALLOWED_TOOLS]

    tools = filter_tools(await client.get_tools())
    system_prompt = (
        "You are a helpful assistant with access to GitHub tools. "
        "Always use the tools to explore the repository rather than making assumptions about its structure. "
        "When asked to generate a mermaid diagram, output ONLY the fenced mermaid block — no prose."
    )
    agent = create_agent(ACTIVE_LLM, tools, system_prompt=system_prompt)

    user_message = MERMAID_PROMPT_TEMPLATE.format(
        owner=owner, repo=repo, branch=branch
    )

    last_response = None
    for attempt in range(1, MAX_RETRIES + 1):
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )
        last_response = result["messages"][-1].content
        mermaid_code = extract_mermaid_code(last_response)

        print(
            f"Attempt {attempt}/{MAX_RETRIES} — mermaid response:\n{last_response}\nExtracted:\n{mermaid_code}\n")

        if mermaid_code is not None:
            return generate_diagrams_diagram(mermaid_code, output_path, ACTIVE_LLM)

        print(
            f"Attempt {attempt}/{MAX_RETRIES}: invalid mermaid format, retrying...")

    raise ValueError(
        f"Failed to get a valid mermaid diagram after {MAX_RETRIES} attempts. "
        f"Last response:\n{last_response}"
    )
