# Repository Guidelines for `mcp-dataportal`

This repository hosts experimental [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/develop/build-server) services that expose Swedish open-data resources through [FastMCP](https://gofastmcp.com/getting-started/welcome) and Starlette. The guidance below establishes repo-wide expectations for future agents and contributors.

## General Principles
- Follow the MCP Python SDK's conventions for structuring servers, resources, prompts, and tools as outlined in the official SDK README.<sup>[1](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file)</sup>
- Treat the Starlette app in `main.py` as an ASGI composition layer; keep business logic inside the `servers/` and `tools/` packages.
- Prefer declarative descriptions and metadata for MCP resources and tools so they can be surfaced cleanly in MCP inspectors.

## Python Style and Quality
- Target Python 3.11+ and adhere to PEP 8 formatting. Use type hints for all public functions and methods.
- Organize imports using the standard library / third-party / local grouping pattern.
- Include docstrings for new modules, classes, and complex functions that clarify the purpose of the tool or resource, especially when referencing Swedish government data sources.
- When adding logic that calls network APIs, wrap request code with clear error handling and timeouts; surface informative MCP errors instead of raw stack traces.

## FastMCP and MCP-Specific Guidance
- Expose new functionality via FastMCP factories (`FastMCP(...)`) and mount tools/resources using descriptive prefixes (e.g., `skatteverket`).
- Use Structured Output schemas when returning complex data from tools so clients can validate responses.<sup>[1](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#structured-output)</sup>
- Prefer asynchronous I/O (e.g., `async def` with `httpx.AsyncClient`) when integrating with external APIs, aligning with Starlette and FastMCP best practices.
- Document any new tools or resources within their module docstrings, including the authoritative data source (link or dataset ID) from dataportal.se when applicable.

## Testing and Local Development
- Use [`uv`](https://docs.astral.sh/uv/) for dependency management. Add new runtime or dev dependencies via `uv add` and commit the updated `uv.lock`.
- Provide lightweight integration tests for non-trivial tools/resources when feasible. Prefer pytest and locate tests under a top-level `tests/` package.
- For manual verification, run the Starlette app with `uvicorn main:app --reload` and inspect mounted MCP servers via `npx @modelcontextprotocol/inspector`.

## Documentation and Communication
- Update `README.md` or create tool-specific markdown references whenever you add notable functionality so downstream agents can discover available datasets.
- Keep module-level TODOs actionable; prefer filing issues over leaving vague comments.

These conventions apply to the entire repository. Add additional `AGENTS.md` files in subdirectories if you need more specific guidance for particular modules or tools.
