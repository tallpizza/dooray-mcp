# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/dooray_mcp/` — core server in `server.py`, HTTP client in `dooray_client.py`.
- Tools: `src/dooray_mcp/tools/` — feature-specific handlers (`tasks.py`, `comments.py`, `tags.py`, `search.py`, `members.py`).
- Entrypoint: `dooray_mcp.server:main` (script `dooray-mcp`), alternative `python -m dooray_mcp.server`.
- Config/examples: `.env.example`, `.mcp.json.example`. Assets: `dooray-api.html`. Root helper: `main.py`.

## Build, Test, and Development Commands
- Install deps: `uv sync` — resolves and installs from `pyproject.toml`/`uv.lock`.
- Run server: `uv run dooray-mcp` or `uv run python -m dooray_mcp.server`.
- Env setup: `cp .env.example .env` then set `DOORAY_API_TOKEN`, `DOORAY_BASE_URL`, `DOORAY_DEFAULT_PROJECT_ID`, `LOG_LEVEL`.
- Claude config (example): `claude mcp add-json dooray "$(cat .mcp.json | jq -c .dooray)"`.

## Coding Style & Naming Conventions
- Python ≥ 3.11, PEP 8, 4-space indentation, type hints required.
- Names: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Tools expose `handle(self, arguments: dict) -> str` and private helpers like `_list_*`, `_create_*`.
- Logging via `logging`; return JSON strings from tools; avoid printing in library code.

## Testing Guidelines
- Framework: `pytest` (suggested). Place tests under `tests/`, named `test_*.py`.
- Write async tests with `pytest.mark.asyncio`. Mock Dooray calls using `httpx.MockTransport`.
- Aim to cover tool branches (e.g., `list`, `create`, error paths) and server error handling.

## Commit & Pull Request Guidelines
- Commits: short, imperative summaries (e.g., "Fix async main function"). Group related changes; include rationale in body when needed.
- PRs: clear description, linked issues, reproduction/verification steps (commands used), and config notes if env vars or `.mcp.json` change.
- Keep diffs focused; update docs/examples when behavior or inputs change.

## Security & Configuration Tips
- Never commit secrets. Keep tokens in `.env` (gitignored). Validate required vars on startup.
- The server uses stdio transport; verify connectivity with `claude mcp list`.
- Prefer raising/propagating errors with informative messages; avoid logging sensitive payloads.
