from typing import Annotated

import httpx
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from fastmcp.server.context import Context

# Documentation urls
API_BASE_URL = "https://skatteverket.entryscape.net/rowstore/dataset/0db155d8-4a46-4b14-aba6-3531ef4141c7"
SWAGGER_URL = "https://swagger.entryscape.com/?url=https%3A%2F%2Fskatteverket.entryscape.net%2Frowstore%2Fdataset%2F0db155d8-4a46-4b14-aba6-3531ef4141c7%2Fswagger"
DATAPORTAL_URL = "https://www.dataportal.se/datasets/6_67905"

taxeringsenhet_typkod_mcp = FastMCP(name="TaxeringsenhetTypkodMCP")


@taxeringsenhet_typkod_mcp.resource(
    title="Typkod API base url",
    uri=API_BASE_URL,
)
def taxeringsenhet_typkod_api_base_url() -> str:
    return "API Base url used for fetching taxeringsenhet typkod"


@taxeringsenhet_typkod_mcp.resource(
    title="Typkod Swagger documentation",
    uri=SWAGGER_URL,
)
def taxeringsenhet_typkod_swagger_url() -> str:
    return "Swagger url to test and view API specification for fetching taxeringsenhet typkod"


@taxeringsenhet_typkod_mcp.resource(
    title="Typkod Dataportal documentation",
    uri=DATAPORTAL_URL,
)
def taxeringsenhet_typkod_dataportal_url() -> str:
    return "Direct link to Sveriges Dataportal where this resource is listed"


class TypKod(BaseModel):
    typkod: str
    beskrivning: str


class TaxeringsenhetReponse(BaseModel):
    next: Annotated[str | None, Field(default="")]
    resultCount: Annotated[int | None, Field(default=0)]
    offset: Annotated[int, Field(ge=0, default=0)]
    limit: Annotated[int, Field(ge=1, le=100, default=10)]
    queryTime: Annotated[int | None, Field(default=0)]
    results: Annotated[list[TypKod], Field(default_factory=list)]


class TaxeringsenhetRequest(BaseModel):
    typkod: Annotated[str | None, Field(default="", max_length=5)] = ""
    beskrivning: Annotated[str | None, Field(default="", max_length=100)] = ""
    _limit: Annotated[int, Field(strict=True, ge=1, le=100, default=10)] = 10
    _offset: Annotated[int, Field(default=0, ge=0)] = 0
    _callback: str | None = None


async def make_request(
    request: TaxeringsenhetRequest,
    ctx: Context,
) -> TaxeringsenhetReponse:
    params = {
        "typkod": request.typkod,
        "beskrivning": request.beskrivning,
        "_limit": request._limit,
        "_offset": request._offset,
        "_callback": request._callback,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    # Remove empty string values
    params = {k: v for k, v in params.items() if v != ""}

    # Strip string values of leading/trailing whitespace
    params = {k: v.strip() if isinstance(v, str) else v for k, v in params.items()}

    await ctx.info(f"info: Making request to {API_BASE_URL} with params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_BASE_URL, params=params, headers={"Accept": "application/json"}
        )

        response.raise_for_status()
        data = response.json()
        await ctx.debug(f"debug: Response data: {data}")

        return TaxeringsenhetReponse(**data)


@taxeringsenhet_typkod_mcp.tool
async def get_taxeringsenhet_typkod(
    typkod: str,
    ctx: Context,
) -> TypKod | str:
    """
    Get a single taxeringsenhet typkod by its typkod.

    Args:
        typkod (str): The typkod to retrieve.

    Returns:
        TypKod | None: The typkod if found, otherwise None.
    """
    await ctx.info(f"info: Getting typkod: {typkod}")
    request = TaxeringsenhetRequest(typkod=typkod, _limit=1)
    response = await make_request(request, ctx)

    if response.results:
        return response.results[0]
    else:
        await ctx.warning(f"warning: Typkod {typkod} not found")
        return ""


@taxeringsenhet_typkod_mcp.tool
async def get_taxeringsenhet_typkod_description(
    description: str,
    ctx: Context,
) -> list[TypKod]:
    """
    Get taxeringsenhet typkoder by their description.

    Args:
        description (str): The description to search for.

    Returns:
        list[TypKod]: A list of matching typkoder.
    """
    await ctx.info(f"info: Getting typkoder with description containing: {description}")
    request = TaxeringsenhetRequest(beskrivning=description, _limit=100)
    response = await make_request(request, ctx)

    if response.results:
        return response.results
    else:
        await ctx.warning(
            f"warning: No typkoder found with description containing '{description}'"
        )
        return []


@taxeringsenhet_typkod_mcp.tool
async def list_taxeringsenhet_typkoder(
    # TODO: implement annotated properly, it will help with validation and defaults
    # limit: Annotated[int, Field(strict=True, ge=1, le=100, default=10)],
    # offset: Annotated[int, Field(default=0, ge=0)],
    limit: int,
    offset: int,
    ctx: Context,
) -> TaxeringsenhetReponse:
    """
    List all taxeringsenhet typkoder with pagination.

    Args:
        limit (int): The maximum number of results to return. Default is 10.
        offset (int): The number of results to skip. Default is 0.

    Returns:
        TaxeringsenhetReponse: The response containing the typkoder.
    """
    await ctx.info(f"info: Listing typkoder with limit={limit}, offset={offset}")
    request = TaxeringsenhetRequest(_limit=limit, _offset=offset)

    return await make_request(request, ctx)
