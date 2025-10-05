"""
An MCP server made specifically for searching and exploring data produced by the
Swedish Parliament (Riksdagen). It has a collection of tools, resources and prompts
to help with tasks related to finding and understanding documents, debates or
past events in the Swedish Parliament.

You can run this server specifically in stdio mode, which is useful for development
and/or local setup.

Run locally with `uv run mcp dev ./servers/riksdagen.py`
Or using uvx with `uvx --from git+https://github.com/asabla/mcp-dataportal python -m servers.riksdagen`
"""

from fastmcp import FastMCP

# Import all tools related to property management (fastighetsförvaltning)
from tools.riksdagen.dokument import dokumentlist_dokument_mcp
from tools.riksdagen.ledamot import ledamot_mcp

RIKSDAGEN_MCP = FastMCP("RiksdagenService")

# Setup all related tools
RIKSDAGEN_MCP.mount(dokumentlist_dokument_mcp, prefix="riksdagen")
RIKSDAGEN_MCP.mount(ledamot_mcp, prefix="riksdagen")


# TODO: fix imports of tools, in order to support stdio mode
# def main():
#     FASTIGHET_MCP.run(transport="stdio")
#
#
# if __name__ == "__main__":
#     main()
