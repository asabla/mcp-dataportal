from typing import Annotated

import httpx
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from fastmcp.server.context import Context

# TODO:
# [ ] Add caching to reduce load on Skatteverket API
# [ ] Add retries with exponential backoff for better reliability
# [ ] Add rate limiting to avoid hitting API limits
# [ ] Add more detailed logging for better traceability
# [ ] Add unit tests and integration tests to ensure code quality
# [ ] Add validation for input parameters to ensure data integrity
# [ ] Simplify models for requests and responses to reduce complexity
# [ ] Add annotated types for better type checking and validation for request parameters
# [ ] Add examples in docstrings for better usability

# Documentation urls
API_BASE_URL = "https://skatteverket.entryscape.net/rowstore/dataset/ed6459d5-66ae-48a7-bcc8-4bd128f719db"
SWAGGER_URL = "https://swagger.entryscape.com/?url=https%3A%2F%2Fskatteverket.entryscape.net%2Frowstore%2Fdataset%2Fed6459d5-66ae-48a7-bcc8-4bd128f719db%2Fswagger"
DATAPORTAL_URL = "https://www.dataportal.se/datasets/6_75017"

fastighetsskatt_avgifter_mcp = FastMCP(name="FastighetsskattAvgifterMCP")


@fastighetsskatt_avgifter_mcp.resource(
    title="Typkod API base url",
    uri=API_BASE_URL,
)
def fastighetsskatt_avgift_api_base_url() -> str:
    return "API Base url used for fetching Fastighetsskatt and avgift"


@fastighetsskatt_avgifter_mcp.resource(
    title="Fastighetsskatt and avgift Swagger documentation",
    uri=SWAGGER_URL,
)
def fastighetsskatt_avgift_swagger_url() -> str:
    return "Swagger url to test and view API specification for fetching fastighetsskatt or avgift"


@fastighetsskatt_avgifter_mcp.resource(
    title="Fastighetsskatt and avgift Dataportal documentation",
    uri=DATAPORTAL_URL,
)
def fastighetsskatt_avgift_dataportal_url() -> str:
    return "Direct link to Sveriges Dataportal where this resource is listed"


class SkattAvgift(BaseModel):
    uppdateringsdatum: Annotated[str | None, Field(default="")]
    gruppering: Annotated[str | None, Field(default="")]
    antal: Annotated[str, Field(default="")]
    statistikterm: Annotated[str | None, Field(default="")]
    belopp: Annotated[str | None, Field(default="")]
    inkomstar: Annotated[str | None, Field(default="")]
    grupperingsvarde: Annotated[str | None, Field(default="", alias="grupperingsvärde")]


class FastighetsskattAvgiftReponse(BaseModel):
    next: Annotated[str | None, Field(default="")]
    resultCount: Annotated[int | None, Field(default=0)]
    offset: Annotated[int, Field(ge=0, default=0)]
    limit: Annotated[int, Field(ge=1, le=100, default=10)]
    queryTime: Annotated[int | None, Field(default=0)]
    results: Annotated[list[SkattAvgift], Field(default_factory=list)]


class FastighetsskattAvgiftRequest(BaseModel):
    uppdateringsdatum: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    gruppering: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    statistikterm: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    antal: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    belopp: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    grupperingsvarde: Annotated[
        str | None,
        Field(
            default="",
            alias="grupperingsvärde",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    inkomstar: Annotated[
        str | None,
        Field(
            default="",
            description="Responses contain only rows with rows that match the provided tuple. Regular expressions may be used",
        ),
    ] = ""
    _limit: Annotated[
        int,
        Field(
            strict=True,
            ge=1,
            le=500,
            default=10,
            description="Size of the result windows, expects a value from 1 to 500. Default is 100",
        ),
    ] = 10
    _offset: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=50,
            description="The offset (results, not pages) to be used when paginating through query results; example: page 3 of a multi page result can be requested with _limit=50 and _offset=100",
        ),
    ] = 0

    class Config:
        # This will allow population by field name or alias
        allow_population_by_field_name = True


async def make_request(
    request: FastighetsskattAvgiftRequest,
    ctx: Context,
) -> FastighetsskattAvgiftReponse:
    params = request.model_dump(by_alias=True, exclude_none=True, exclude_unset=True)

    # Remove None values
    # params = {k: v for k, v in params.items() if v is not None}

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

        return FastighetsskattAvgiftReponse(**data)


@fastighetsskatt_avgifter_mcp.tool
async def search_fastighetsskatt_avgift(
    uppdateringsdatum: str | None,
    gruppering: str | None,
    statistikterm: str | None,
    antal: str | None,
    belopp: str | None,
    grupperingsvarde: str | None,
    inkomstar: str | None,
    _limit: int,
    _offset: int,
    ctx: Context,
) -> FastighetsskattAvgiftReponse:
    """
    Search for fastighetsskatt and avgift based on various parameters.

    Args:
        uppdateringsdatum (str | None): The update date to filter by.
        gruppering (str | None): The grouping to filter by.
        statistikterm (str | None): The statistical term to filter by.
        antal (str | None): The count to filter by.
        belopp (str | None): The amount to filter by.
        grupperingsvarde (str | None): The grouping value to filter by.
        inkomstar (str | None): The income years to filter by.
        _limit (int): The maximum number of results to return. Default is 10.
        _offset (int): The number of results to skip. Default is 0.
        ctx (Context): The context for logging and other purposes.

    Returns:
        FastighetsskattAvgiftReponse: The response containing the fastighetsskatt and avgift.
    """

    params = FastighetsskattAvgiftRequest(
        uppdateringsdatum=uppdateringsdatum,
        gruppering=gruppering,
        statistikterm=statistikterm,
        antal=antal,
        belopp=belopp,
        grupperingsvarde=grupperingsvarde,
        inkomstar=inkomstar,
        _limit=_limit,
        _offset=_offset,
    )
    await ctx.info(f"info: Searching fastighetsskatt and avgift with params={params}")
    return await make_request(params, ctx)


@fastighetsskatt_avgifter_mcp.tool
async def list_fastighetsskatt_avgift(
    # TODO: implement annotated properly, it will help with validation and defaults
    # limit: Annotated[int, Field(strict=True, ge=1, le=100, default=10)],
    # offset: Annotated[int, Field(default=0, ge=0)],
    limit: int,
    offset: int,
    ctx: Context,
) -> FastighetsskattAvgiftReponse:
    """
    List all fastighetsskatt and avgift with pagination.

    Args:
        limit (int): The maximum number of results to return. Default is 10.
        offset (int): The number of results to skip. Default is 0.
    Returns:
        FastighetsskattAvgiftReponse: The response containing the fastighetsskatt and avgift.
    """
    await ctx.info(f"info: Listing typkoder with limit={limit}, offset={offset}")
    request = FastighetsskattAvgiftRequest(_limit=limit, _offset=offset)

    return await make_request(request, ctx)
