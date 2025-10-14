"""
MCP tool for listing Riksdagens ledamöter via dokumentlistan (avd=ledamot).

This module exposes a FastMCP tool that queries the open API at
"https://data.riksdagen.se/dokumentlista/" with avd=ledamot to retrieve
entries representing riksdagsledamöter. The results are parsed into Pydantic
models so MCP clients can reliably consume structured output.

Data sources
- Dokumentlista: https://data.riksdagen.se/dokumentlista/
- Dataportal:    https://www.dataportal.se/dataservice/98_3022

Notes for MCP usage
- The tool returns a `LedamotLista` model on success or an empty string if no
  results were found. Clients that support structured output can validate the
  response against the models in this module.
- Network operations are async and use httpx with a timeout.
- Swedish identifiers are preserved to match the upstream API.
"""

from typing import Annotated

import httpx
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from fastmcp.server.context import Context

# Documentation and dataset URLs
API_BASE_URL = "https://data.riksdagen.se/dokumentlista/"
LEDAMOT_BASE_URL = API_BASE_URL  # same base, but with avd=ledamot
SWAGGER_URL = ""
DATAPORTAL_URL = "https://www.dataportal.se/dataservice/98_3022"

ledamot_mcp = FastMCP(name="LedamotListaMCP")


class Uppgift(BaseModel):
    """Nyckel‑värde uppgifter knutna till en person.

    Fälten och koderna kommer från Riksdagens API och kan variera.
    """

    kod: Annotated[str | None, Field(default=None)]
    uppgift: Annotated[str | None, Field(default=None)]
    typ: Annotated[str | None, Field(default=None)]

    class Config:
        extra = "allow"


class PersonUppgift(BaseModel):
    """Container för personuppgifter (lista av `Uppgift`)."""

    uppgift: Annotated[list[Uppgift] | None, Field(default=None)]

    class Config:
        extra = "allow"


class Uppdrag(BaseModel):
    """Uppdrag/roller som en ledamot haft i olika organ."""

    organ_kod: Annotated[str | None, Field(default=None)]
    roll_kod: Annotated[str | None, Field(default=None)]
    roll_kod_en: Annotated[str | None, Field(default=None)]
    ordningsnummer: Annotated[str | None, Field(default=None)]
    status: Annotated[str | None, Field(default=None)]
    typ: Annotated[str | None, Field(default=None)]
    from_: Annotated[str | None, Field(default=None, alias="from")]
    tom: Annotated[str | None, Field(default=None)]
    uppgift: Annotated[str | None, Field(default=None)]
    uppgift_en: Annotated[str | None, Field(default=None)]
    organ_sortering: Annotated[str | None, Field(default=None)]
    sortering: Annotated[str | None, Field(default=None)]

    class Config:
        extra = "allow"
        allow_population_by_field_name = True


class PersonUppdrag(BaseModel):
    """Container för uppdrag (lista av `Uppdrag`)."""

    uppdrag: Annotated[list[Uppdrag] | None, Field(default=None)]

    class Config:
        extra = "allow"


class AvdelningList(BaseModel):
    """Lista av avdelningar kopplade till ett objekt."""

    avdelning: Annotated[list[str] | None, Field(default=None)]

    class Config:
        extra = "allow"


class LedamotItem(BaseModel):
    """Ett enskilt dokument/objekt från dokumentlistan för en ledamot.

    Modellen är medvetet permissiv (extra = "allow") då API:t kan returnera
    ytterligare fält. Endast fält som är vanliga/nyttiga för klienter listas
    här för att underlätta strukturerad output.
    """

    # Common dokumentlista fields
    traff: Annotated[str | None, Field(default=None)]
    domain: Annotated[str | None, Field(default=None)]
    database: Annotated[str | None, Field(default=None)]
    datum: Annotated[str | None, Field(default=None)]
    id: Annotated[str | None, Field(default=None)]
    publicerad: Annotated[str | None, Field(default=None)]
    systemdatum: Annotated[str | None, Field(default=None)]
    undertitel: Annotated[str | None, Field(default=None)]
    kalla: Annotated[str | None, Field(default=None)]
    kall_id: Annotated[str | None, Field(default=None)]  # present in ledamot list
    lang: Annotated[str | None, Field(default=None)]
    url: Annotated[str | None, Field(default=None)]
    relurl: Annotated[str | None, Field(default=None)]
    titel: Annotated[str | None, Field(default=None)]
    status: Annotated[str | None, Field(default=None)]
    score: Annotated[str | None, Field(default=None)]
    struktur: Annotated[str | None, Field(default=None)]
    debattnamn: Annotated[str | None, Field(default=None)]
    dokumentnamn: Annotated[str | None, Field(default=None)]

    # Search-data blob (keep permissive)
    sokdata: Annotated[dict | None, Field(default=None)]

    # Avdelningar
    avdelning: Annotated[str | None, Field(default=None)]  # single string
    avdelningar: Annotated[AvdelningList | None, Field(default=None)]

    # Member-specific convenience fields observed in the API
    parti: Annotated[str | None, Field(default=None)]
    efternamn: Annotated[str | None, Field(default=None)]
    tilltalsnamn: Annotated[str | None, Field(default=None)]
    bokstav: Annotated[str | None, Field(default=None)]
    iort: Annotated[str | None, Field(default=None)]
    fodd_ar: Annotated[str | None, Field(default=None)]
    valkrets: Annotated[str | None, Field(default=None)]

    # Nested person data
    personuppgift: Annotated[PersonUppgift | None, Field(default=None)]
    personuppdrag: Annotated[PersonUppdrag | None, Field(default=None)]

    # Notis/summary
    summary: Annotated[str | None, Field(default=None)]
    notisrubrik: Annotated[str | None, Field(default=None)]
    notis: Annotated[str | None, Field(default=None)]

    class Config:
        extra = "allow"


class LedamotLista(BaseModel):
    """Rotobjekt för dokumentlistan när `avd=ledamot`.

    Fält med alias (t.ex. "@sida") följer API:ts svar och exponeras som
    Python‑fält med samma namn när modellen serialiseras med alias.
    """

    ms: Annotated[str | None, Field(default=None, alias="@ms")]
    version: Annotated[str | None, Field(default=None, alias="@version")]
    q: Annotated[str | None, Field(default=None, alias="@q")]
    varning: Annotated[str | None, Field(default=None, alias="@varning")]
    datum: Annotated[str | None, Field(default=None, alias="@datum")]
    nasta_sida: Annotated[str | None, Field(default=None, alias="@nasta_sida")]
    sida: Annotated[str | None, Field(default=None, alias="@sida")]
    sidor: Annotated[str | None, Field(default=None, alias="@sidor")]
    traff_fran: Annotated[str | None, Field(default=None, alias="@traff_fran")]
    traff_till: Annotated[str | None, Field(default=None, alias="@traff_till")]
    traffar: Annotated[str | None, Field(default=None, alias="@traffar")]
    # TODO: remove me?
    # Ignored fields for now
    # dPre: Annotated[int | None, Field(default=None, alias="@dPre")]
    # dSol: Annotated[int | None, Field(default=None, alias="@dSol")]
    # dDt: Annotated[int | None, Field(default=None, alias="@dDt")]
    # dR: Annotated[int | None, Field(default=None, alias="@dR")]
    facettlista: Annotated[dict | None, Field(default=None)]
    dokument: Annotated[list[LedamotItem] | None, Field(default=None, alias="dokument")]

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


class LedamotResponse(BaseModel):
    """Top‑level svar som omsluter `dokumentlista`."""

    dokumentlista: Annotated[LedamotLista | None, Field(default=None)]


async def _make_request(
    ctx: Context,
    *,
    sok: str | None = None,  # free-text search
    datum: str | None = None,  # from-date YYYY-MM-DD
    tom: str | None = None,  # to-date   YYYY-MM-DD
    sort: str = "rel",
    sortorder: str = "desc",
    p: int | None = None,  # page
    pagesize: int | None = None,  # optional page size (if supported)
) -> LedamotResponse:
    """Anropa Riksdagens dokumentlista och returnera ett parsat svar.

    Parametrarna speglar det publika MCP‑verktyget och skickas vidare som
    query‑parametrar. Vid HTTP‑fel kastas ett undantag från `httpx`.
    """
    params: dict[str, str] = {
        "avd": "ledamot",
        "sort": sort,
        "sortorder": sortorder,
        "utformat": "json",
    }
    if sok:
        params["sok"] = sok
    if datum:
        params["datum"] = datum
    if tom:
        params["tom"] = tom
    if p is not None:
        params["p"] = str(p)
    if pagesize is not None:
        # the API sometimes supports "pagesize" or "z" – keep to pagesize if available
        params["pagesize"] = str(pagesize)

    await ctx.info(f"info: Making request to {LEDAMOT_BASE_URL} with params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            LEDAMOT_BASE_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        await ctx.debug(f"debug: Response keys: {list(data.keys())}")
        return LedamotResponse(**data)


@ledamot_mcp.tool(
    name="riksdagen_ledamot_list",
    description=(
        "Listar poster från Riksdagens dokumentlista för avd=ledamot. "
        "Använd för att söka efter ledamöter och deras metadata."
    ),
)
async def list_members_ledamot(
    ctx: Context,
    sok: str | None,  # free-text
    datum: str | None,  # from-date YYYY-MM-DD
    tom: str | None,  # to-date   YYYY-MM-DD
    p: int | None,  # page
    pagesize: int | None,  # optional page size (if supported)
    sort: str = "rel",
    sortorder: str = "desc",
) -> LedamotLista | str:
    """Lista ledamöter via dokumentlistan (avd=ledamot) som MCP‑verktyg.

    Parametrar
    - `sok`: Fritext (namn, parti, m.m.).
    - `datum`: Från‑datum i format `YYYY-MM-DD`.
    - `tom`: Till‑datum i format `YYYY-MM-DD`.
    - `sort`: Sorteringsfält (t.ex. `rel`).
    - `sortorder`: `asc` eller `desc` (standard `desc`).
    - `p`: Sidnummer (1‑baserat).
    - `pagesize`: Antal resultat per sida om endpointen stödjer det.

    Returnerar
    - `LedamotLista` vid träffar, annars tom sträng om inga poster hittas.

    MCP‑kontext
    - Funktionens annoteringar och Pydantic‑modeller möjliggör strukturerad
      output i klienter som validerar svarens form.
    - `ctx` används för att logga informations‑, varnings‑ och debug‑meddelanden
      till MCP‑klienten.
    """
    await ctx.info(
        f"info: Getting ledamöter (sok={sok!r}, datum={datum!r}, tom={tom!r}, "
        f"sort={sort!r}, sortorder={sortorder!r}, p={p!r}, pagesize={pagesize!r})"
    )

    response = await _make_request(
        ctx,
        sok=sok,
        datum=datum,
        tom=tom,
        sort=sort,
        sortorder=sortorder,
        p=p,
        pagesize=pagesize,
    )

    if response.dokumentlista:
        return response.dokumentlista
    else:
        await ctx.warning("warning: No ledamöter found with the provided filters")
        return ""
