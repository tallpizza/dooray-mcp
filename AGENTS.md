# Repository Guidelines

## Project Structure & Module Organization

- Core implementation lives in `src/dooray_mcp/`; `server.py` holds the MCP entrypoint and `dooray_client.py` wraps the Dooray HTTP API.
- Tool handlers reside in `src/dooray_mcp/tools/` with focused modules (`tasks.py`, `comments.py`, `tags.py`, `search.py`, `members.py`).
- Configuration samples (`.env.example`, `.mcp.json.example`) and API reference (`dooray-api.html`) sit in the project root; `main.py` provides local helper utilities.
- Tests should go under `tests/`, mirroring the package layout for easy discovery.

## Build, Test, and Development Commands

- `uv sync` — install and lock Python dependencies from `pyproject.toml`/`uv.lock`.
- `uv run dooray-mcp` — launch the MCP server via the console script.
- `uv run python -m dooray_mcp.server` — alternative entrypoint useful when debugging.
- `pytest` — execute the test suite; add `-k pattern` to narrow scope while iterating.

## Coding Style & Naming Conventions

- Target Python 3.11+, 4-space indentation, and PEP 8 compliance throughout.
- Require type hints on public interfaces; prefer explicit `TypedDict`/`Protocol` when shaping Dooray payloads.
- Naming: modules/functions use `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Avoid prints in library code; rely on `logging` with configurable `LOG_LEVEL`.

## Testing Guidelines

- Use `pytest` with async tests marked via `@pytest.mark.asyncio`.
- Stub Dooray HTTP calls using `httpx.MockTransport` to keep tests deterministic.
- Name test files `test_*.py` and mirror the tool or component under test.
- Run `pytest --maxfail=1` before pushing to catch regressions quickly.
- Manual tool validation: `python run-tool.py dooray_tasks --action list` launches the MCP server with `uv run dooray-mcp`, confirms the tool is registered, and executes the specified action; swap in other tool names and flags as needed. 사용 가능한 도구는 `python run-tool.py --list-tools`로 확인할 수 있습니다.

## Commit & Pull Request Guidelines

- Write commits in imperative mood (e.g., "Add task list handler"); group related changes and explain rationale in the body when useful.
- Pull requests should summarize behavior changes, link related issues, and call out new env vars or config updates.
- Include reproduction or verification steps (commands executed) and note any screenshots or logs stored externally.

## Security & Configuration Tips

- Copy `.env.example` to `.env`, then set `DOORAY_API_TOKEN`, `DOORAY_BASE_URL`, `DOORAY_DEFAULT_PROJECT_ID`, and `LOG_LEVEL`.
- Never commit secrets; ensure sensitive values stay outside tracked files.
- Validate connectivity with `claude mcp list` after launching the server to confirm stdio transport is working.

언제나 한글로 답해줘
