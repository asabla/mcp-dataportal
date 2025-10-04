from starlette.applications import Starlette
from starlette.routing import Mount

from servers.fastigheter import FASTIGHET_MCP

app = Starlette(routes=[Mount("/fastigheter", app=FASTIGHET_MCP.sse_app())])
