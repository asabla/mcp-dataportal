"""
MCP‑verktyg för att lista och hämta kalenderhändelser från Riksdagen.

Detta modul definierar två FastMCP‑verktyg:
- list_kalender_handelser: listar händelser via dokumentlistan (avd=kalender)
- fetch_kalender_handelse: hämtar en enskild händelse/dokument i text/html/json

Modulen använder Riksdagens öppna API och returnerar Pydantic‑modeller
(`DokumentLista`, `DokumentDetaljResponse`) för strukturerad output i MCP‑klienter.

Datakällor
- Dokumentlista: https://data.riksdagen.se/dokumentlista/
- Dokument:      https://data.riksdagen.se/dokument/
- Dataportal:    https://www.dataportal.se/dataservice/98_3019

MCP‑noteringar
- Nätverksanrop görs asynkront med httpx och tidsgräns.
- Svenska fält‑ och parameternamn behålls för att spegla API:t.
"""

from typing import Literal

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from tools.riksdagen.models import (
    DokumentResponse,
    DokumentDetaljResponse,
    DokumentLista,
)

# Documentation and dataset URLs
API_BASE_URL = "https://data.riksdagen.se/dokumentlista/"
DOCUMENT_BASE_URL = "https://data.riksdagen.se/dokument/"
SWAGGER_URL = ""
DATAPORTAL_URL = "https://www.dataportal.se/dataservice/98_3019"

kalender_handelser_mcp = FastMCP(name="KalenderHandelserMCP")


def _normalize_document_url(value: str, fmt: Literal["text", "html", "json"]) -> str:
    """Normalisera dokumentsökväg till en fullständig URL i önskat format.

    Accepterar antingen ett dok_id (t.ex. "HD096") eller en URL (absolut,
    protokoll‑relativ eller relativ) och returnerar en URL mot
    `https://data.riksdagen.se/dokument/` med rätt ändelse.

    Exempel
    - "HD096" + fmt="text"  → https://data.riksdagen.se/dokument/HD096.text
    - "//data.riksdagen.se/dokument/HD096.html" + fmt="json" → …/HD096.json
    - "/dokument/HD096.txt"  → normaliseras till ".text" och önskat format
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
    """Anropa dokumentlistan (avd=kalender) och returnera parsad respons.

    Parametrar speglar Riksdagens API och vidarebefordras som query‑parametrar.
    Vid HTTP‑fel kastas undantag från httpx. Normalt används `utformat=json`.
    """
    params: dict[str, str] = {
        "avd": "kalender",
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


@kalender_handelser_mcp.tool(
    name="riksdagen_kalender_list",
    description=(
        "Listar kalenderhändelser via Riksdagens dokumentlista (avd=kalender) "
        "med stöd för filtrering (doktyp, rm, datum, organ, sort)."
    ),
)
async def list_kalender_handelser(
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
    """Lista kalenderhändelser med valfria filter som MCP‑verktyg.

    Parametrar
    - `doktyp`: Typkod (t.ex. utskottsmöte), enligt API:s doktyp.
    - `sok`: Fritext.
    - `rm`: Riksmöte, t.ex. `2023/24`.
    - `datum`: Från‑datum `YYYY-MM-DD`.
    - `tom`: Till‑datum `YYYY-MM-DD`.
    - `organ`: Organ/utskott (kod).
    - `sort`: Sorteringsfält (standard `rel`).
    - `sortorder`: `asc` eller `desc` (standard `desc`).

    Returnerar
    - `DokumentLista` vid träffar, annars tom sträng om inga poster hittas.

    MCP‑kontext
    - Strukturerad output via Pydantic‑modeller underlättar klientvalidering.
    - `ctx` används för loggning av info/varning/debug till MCP‑klienten.
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


@kalender_handelser_mcp.tool(
    name="riksdagen_kalender_fetch",
    description=(
        "Hämtar en specifik kalenderhändelse/dokument i önskat format (text/html/json) "
        "givet ett dok_id eller en URL."
    ),
)
async def fetch_kalender_handelse(
    ctx: Context,
    dok_id_or_url: str,
    fmt: Literal["text", "html", "json"] = "text",
) -> DokumentDetaljResponse | str:
    """Hämta dokumentinnehåll eller metadata för en enskild händelse.

    Parametrar
    - `dok_id_or_url`: Antingen ett `dok_id` (t.ex. `HD096`) eller en URL
      (protokoll‑relativ/relativ/absolut) till dokumentet.
    - `fmt`: `text` | `html` | `json` (standard `text`).

    Returnerar
    - För `text` eller `html`: dokumentinnehållet som sträng.
    - För `json`: `DokumentDetaljResponse` med parsat JSON‑innehåll.
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
