from starlette.applications import Starlette
from starlette.routing import Mount

from servers.fastigheter import FASTIGHET_MCP
from servers.riksdagen import RIKSDAGEN_MCP

app = Starlette(
    routes=[
        Mount("/fastigheter", app=FASTIGHET_MCP.sse_app()),
        Mount("/riksdagen", app=RIKSDAGEN_MCP.sse_app()),
    ]
)
