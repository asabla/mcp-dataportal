from typing import Literal

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from tools.riksdagen.models import (
    DokumentResponse,
    DokumentDetaljResponse,
    DokumentLista,
)

# Documentation urls
API_BASE_URL = "https://data.riksdagen.se/dokumentlista/"
DOCUMENT_BASE_URL = "https://data.riksdagen.se/dokument/"
SWAGGER_URL = ""
DATAPORTAL_URL = "https://www.dataportal.se/dataservice/98_3023"

dokumentlist_dokument_mcp = FastMCP(name="DokumentlistaDokumentMCP")


def _normalize_document_url(value: str, fmt: Literal["text", "html", "json"]) -> str:
    """
    Accepts either a dok_id (e.g., 'HD096') or a URL (absolute or protocol-relative),
    and returns a fully-qualified URL for the requested format.
    """
    if not value:
        raise ValueError("Missing dok_id or document URL")

    # If it's already a URL, normalize protocol and return
    if value.startswith("http://") or value.startswith("https://"):
        url = value
    elif value.startswith("//"):
        url = "https:" + value
    elif value.startswith("/"):
        # Some fields are relative to www.riksdagen.se or data.riksdagen.se;
        # prioritise data.riksdagen.se for content endpoints.
        # If the caller passed a rel URL to /dokument/..., join to data base:
        url = "https://data.riksdagen.se" + value
    else:
        # Treat as dok_id
        url = f"{DOCUMENT_BASE_URL}{value}.{fmt}"

    # If the caller passed a URL to a different format, coerce to requested format
    if "/dokument/" in url:
        if url.endswith(".text") or url.endswith(".html") or url.endswith(".json"):
            url = url.rsplit(".", 1)[0] + f".{fmt}"
        # Some listings use ".txt" – normalise to ".text"
        if url.endswith(".txt"):
            url = url[:-4] + ".text"

    return url


async def make_request(
    ctx: Context,
    doktyp: str | None = None,
    *,
    sok: str | None = None,  # free-text search
    rm: str | None = None,  # riksmöte, e.g. "2023/24"
    datum: str | None = None,  # from-date YYYY-MM-DD
    tom: str | None = None,  # to-date   YYYY-MM-DD
    organ: str | None = None,  # committee/organ code
    sort: str = "rel",
    sortorder: str = "desc",
    utformat: str = "json",
) -> DokumentResponse:
    params: dict[str, str] = {
        "avd": "dokument",
        "sort": sort,
        "sortorder": sortorder,
        "utformat": utformat,
    }
    if doktyp:
        params["doktyp"] = doktyp
    if sok:
        params["sok"] = sok
    if rm:
        params["rm"] = rm
    if datum:
        params["datum"] = datum
    if tom:
        params["tom"] = tom
    if organ:
        params["org"] = organ

    await ctx.info(f"info: Making request to {API_BASE_URL} with params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_BASE_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        await ctx.debug(f"debug: Response keys: {list(data.keys())}")
        return DokumentResponse(**data)


@dokumentlist_dokument_mcp.tool
async def list_documents(
    ctx: Context,
    doktyp: str | None = None,
    sok: str | None = None,  # free-text
    rm: str | None = None,  # riksmöte, e.g. "2023/24"
    datum: str | None = None,  # from-date YYYY-MM-DD
    tom: str | None = None,  # to-date   YYYY-MM-DD
    organ: str | None = None,  # committee/organ code
    sort: str = "rel",
    sortorder: str = "desc",
) -> DokumentLista | str:
    """
    List documents from Riksdagens 'dokumentlista' with optional filters.

    Args:
        doktyp:   Document type code (e.g., 'mot', 'prop', 'bet', 'prot').
        sok:      Free-text query.
        rm:       Riksmöte season, e.g. '2023/24'.
        datum:    From-date (YYYY-MM-DD).
        tom:      To-date   (YYYY-MM-DD).
        organ:    Committee/organ code.
        sort:     Sort field (default 'rel').
        sortorder:'asc' or 'desc' (default 'desc').
    """
    await ctx.info(
        f"info: Getting documents (doktyp={doktyp!r}, sok={sok!r}, rm={rm!r}, "
        f"datum={datum!r}, tom={tom!r}, organ={organ!r}, sort={sort!r}, sortorder={sortorder!r})"
    )

    response = await make_request(
        ctx,
        doktyp=doktyp,
        sok=sok,
        rm=rm,
        datum=datum,
        tom=tom,
        organ=organ,
        sort=sort,
        sortorder=sortorder,
    )

    if response.dokumentlista:
        return response.dokumentlista
    else:
        await ctx.warning("warning: No documents found with the provided filters")
        return ""


@dokumentlist_dokument_mcp.tool
async def fetch_document(
    ctx: Context,
    dok_id_or_url: str,
    fmt: Literal["text", "html", "json"] = "text",
) -> DokumentDetaljResponse | str:
    """
    Fetch a specific document's content or metadata.

    Args:
        dok_id_or_url: Either a dok_id like 'HD096' or a URL such as
                       '//data.riksdagen.se/dokument/HD096.text' or
                       '/dokument/HD096.html' or a full https URL.
        fmt:           'text' | 'html' | 'json'. Defaults to 'text'.

    Returns:
        - For 'text' or 'html': the response body as a string.
        - For 'json': DokumentDetaljResponse with the parsed JSON.
    """
    try:
        url = _normalize_document_url(dok_id_or_url, fmt)
    except Exception as e:
        await ctx.error(f"error: {e}")
        return ""

    await ctx.info(f"info: Fetching document from {url}")

    headers = {
        "Accept": "application/json"
        if fmt == "json"
        else "text/plain, text/html; q=0.9, */*; q=0.8"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=30.0)
        resp.raise_for_status()

        if fmt == "json":
            data = resp.json()
            await ctx.debug(f"debug: Document JSON keys: {list(data.keys())}")
            # The single-document endpoint wraps content under 'dokument'
            return DokumentDetaljResponse(**data)
        else:
            text = resp.text
            # Keep log short to avoid flooding logs with full documents
            await ctx.debug(f"debug: Received {len(text)} characters")
            return text
