## GitHub Dashboard Project

A small toolkit that analyzes GitHub repositories and surfaces architecture, dependency, and compliance insights via a web dashboard.

**Key features**
- Repository structure analysis and recommendations
- LLM-based compliance checklist generation
- Automated architecture diagram generation
- Web UI for browsing analyses and visualizations

**Repository layout**
- `backend/` — Python services, analyzers and API
  - `main.py` — backend entrypoint (FastAPI)
  - `compliance_checker/` — compliance checks, fetchers, runners
  - `repo_analyzer/` — repo analysis logic and prompts
  - `llm_compliance_checker/` — LLM checklist and model helpers
  - `diagram_agent/`, `diagram_cache/` — architecture diagram generation support
- `frontend/` — React (Vite) web UI
  - `src/` — React components, hooks, utils
  - `public/` — static assets

## Quick start (Docker Compose)

This repository includes a `docker-compose.yml` to run the backend and frontend together for development or demo purposes.

1. Build and start services:

```bash
docker-compose up --build
```

2. Open the frontend at `http://localhost:5173` and the backend API at `http://localhost:8000` (defaults).

## Developer setup (local)

Backend (Python):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Frontend (development):

```bash
cd frontend
npm install
npm run dev
```

## Environment & configuration
- Backend: environment variables and config are read in `backend/main.py` and module-level config files. Check each subpackage for additional env vars (API keys, model settings).
- Frontend: see `frontend/package.json` and `vite.config.js` for dev server settings.

## API & UI
- The backend exposes REST endpoints for repository analysis and compliance checks (see `backend/main.py`).
- The frontend provides UI components for scanning repos, viewing results, and generating diagrams (check `frontend/src/components`).

## API Examples
Below are common API endpoints with example `curl` requests and parameter descriptions. Replace `<owner>`, `<repo>`, `<branch>`, `<path>`, and `<token>` with real values.

- Get repository tree (detailed, used by frontend):

```bash
curl "http://localhost:8000/api/tree?owner=<owner>&repo=<repo>&branch=main&token=<token>"
```
Parameters: `owner`, `repo`, optional `branch` (default `main`), `token` (GitHub PAT).

- Get compact nested tree:

```bash
curl "http://localhost:8000/api/tree-compact?owner=<owner>&repo=<repo>&branch=main&token=<token>"
```

- Classify a directory (deterministic):

```bash
curl -X POST "http://localhost:8000/api/classify-directory?owner=<owner>&repo=<repo>&branch=main&path=src&token=<token>"
```
Returns the detected `category` for `path` (one of `frontend`, `backend`, `infrastructure`, `shared`, `docs`).

- Run deterministic dynamic compliance checks:

```bash
curl -X POST "http://localhost:8000/api/check-dynamic?owner=<owner>&repo=<repo>&branch=main&path=src&token=<token>"
```

- Run deterministic specific checks (select tests by index):

```bash
curl -X POST "http://localhost:8000/api/check-specific?owner=<owner>&repo=<repo>&branch=main&path=src&category=backend&tests=1&tests=3&token=<token>"
```
`tests` is a repeated query parameter listing 1-based test indices to run.

- Run full LLM-based comprehensive analysis:

```bash
curl -X POST "http://localhost:8000/api/analyze-repo/comprehensive?owner=<owner>&repo=<repo>&branch=main&github_token=<token>&groq_api_key=<groq_key>"
```

- Generate or fetch cached architecture diagram (returns PNG):

```bash
curl -X POST "http://localhost:8000/api/diagram/architecture_diagram?owner=<owner>&repo=<repo>&branch=main&refresh=false&github_token=<token>" --output diagram.png
```

- Get file extension summary:

```bash
curl "http://localhost:8000/api/repo/file-summary?owner=<owner>&repo=<repo>&branch=main&github_token=<token>"
```

## License

This project is licensed under the MIT License — see the `LICENSE` file in the repository root for details.

## Repository Setup

1. Clone the repository:

```bash
git clone <repo-url>
cd github_dashboard_project
```

2. Create a branch for your work:

```bash
git checkout -b feat/your-feature-name
```

## Installation

Prerequisites:
- Docker & Docker Compose (recommended for quick start)
- Python 3.10+ for local backend development
- Node.js 18+ and npm for local frontend development

Install and run with Docker Compose (recommended):

```bash
docker-compose up --build
```

Local backend install (optional):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Local frontend install (optional):

```bash
cd frontend
npm install
npm run dev
```

Environment variables:
- Set `GITHUB_PERSONAL_ACCESS_TOKEN` or pass `token`/`github_token` to endpoints when calling GitHub API.
- Set any LLM provider keys (Anthropic, Groq, etc.) as environment variables or pass via query parameters where supported.

## Contributing Guidelines

- Please open an issue before starting large work so we can discuss scope.
- Create a branch named `feat/...`, `fix/...`, or `docs/...` and make focused changes.
- Run linters/formatters and add tests for new functionality.
- Keep PRs small and include a clear description of changes.
- Use imperative commit messages (e.g., "Add API examples to README").

If you'd like, I can also create a `CONTRIBUTING.md` with these rules and a simple PR template.