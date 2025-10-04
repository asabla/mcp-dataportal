"""
An MCP server made specifically for property management (fastighetsförvaltning).
It has a collection of tools, resources and prompts to help with tasks related to
real estate, property tax, and other aspects of property management in Sweden.

You can run this server specifically in stdio mode, which is useful for development
and/or local setup.

Run locally with `uv run mcp dev ./servers/fastigheter.py`
Or using uvx with `uvx --from git+https://github.com/asabla/mcp-dataportal python -m servers.fastigheter`
"""

from fastmcp import FastMCP

# Import all tools related to property management (fastighetsförvaltning)
from tools.skatteverket.typkoder_taxeringsenheter import taxeringsenhet_typkod_mcp

FASTIGHET_MCP = FastMCP("FastighetsforvaltningService")

# Setup all related tools
FASTIGHET_MCP.mount(taxeringsenhet_typkod_mcp, prefix="skatteverket")


# TODO: fix imports of tools, in order to support stdio mode
# def main():
#     FASTIGHET_MCP.run(transport="stdio")
#
#
# if __name__ == "__main__":
#     main()
