# Repository Guidelines

This repository hosts experimental Model Context Protocol (MCP) services that expose Swedish open‑data via FastMCP and Starlette. Use this guide to contribute consistent, testable changes.

## Project Structure & Module Organization

- `main.py` — ASGI composition layer; mount MCP servers and routes only.
- `servers/` — MCP servers, resources, prompts, and tool factories (per data source).
- `tools/` — Shared tool implementations/helpers reusable across servers.
- `tests/` — Pytest suite; mirror package structure (e.g., `tests/servers/test_skatteverket.py`).
- `README.md` — Quick start and dataset discovery notes.

Keep business logic inside `servers/` and `tools/`; keep `main.py` thin.

## Build, Test, and Development Commands

- `uv sync` — Install/resolve dependencies from `pyproject.toml` into `.venv`.
- `uv add <package>` — Add a dependency and update `uv.lock`.
- `uv run uvicorn main:app --reload` — Run the Starlette app for manual inspection.
- `uv run pytest -q` — Run tests. Add `-k <pattern>` for focused runs.
- `npx @modelcontextprotocol/inspector` — Inspect mounted MCP tools/resources locally.

## Coding Style & Naming Conventions

- Python 3.11+, PEP 8, 4‑space indentation, type hints for public APIs.
- Imports grouped: standard library / third‑party / local.
- Modules and functions: snake_case; classes: CapWords.
- FastMCP: expose via `FastMCP(...)` and descriptive prefixes (e.g., `skatteverket_*`).
- Document tools/resources with module docstrings, including authoritative data source links (e.g., dataportal.se dataset IDs).

## Testing Guidelines

- Framework: `pytest`. Place tests under `tests/` named `test_*.py`.
- Prefer lightweight integration tests for tools/resources; mock network with `httpx` utilities.
- Keep tests deterministic and fast; validate Structured Output shapes.

## Commit & Pull Request Guidelines

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- PRs must include: purpose, linked issues, how to verify, and any screenshots/logs. Update `README.md` when adding notable datasets or endpoints.

## MCP/FastMCP Notes

- Prefer async I/O (`async def` with `httpx.AsyncClient`) and set timeouts.
- Wrap external calls with clear error handling; surface informative MCP errors.
- Use Structured Output schemas for complex results so clients can validate.

## Security & Configuration Tips

- Do not commit secrets; read config via environment variables.
- Validate inputs; sanitize parameters passed to external APIs.
- Fail gracefully with actionable messages; avoid leaking stack traces to clients.

