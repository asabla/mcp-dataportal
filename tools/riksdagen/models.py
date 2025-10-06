from typing import Annotated
from pydantic import BaseModel, Field


class SokData(BaseModel):
    brodsmula: Annotated[str | None, Field(default=None)]
    kalenderprio: Annotated[str | None, Field(default=None)]
    pari_kod: Annotated[str | None, Field(default=None)]
    parti_epost: Annotated[str | None, Field(default=None)]
    parti_logotyp_img_alt: Annotated[str | None, Field(default=None)]
    parti_logotyp_img_id: Annotated[str | None, Field(default=None)]
    parti_logotyp_img_url: Annotated[str | None, Field(default=None)]
    parti_mandat: Annotated[str | None, Field(default=None)]
    parti_namn: Annotated[str | None, Field(default=None)]
    parti_telefon: Annotated[str | None, Field(default=None)]
    parti_telefontider: Annotated[str | None, Field(default=None)]
    parti_website_namn: Annotated[str | None, Field(default=None)]
    parti_website_url: Annotated[str | None, Field(default=None)]
    soktyp: Annotated[str | None, Field(default=None)]
    statusrad: Annotated[str | None, Field(default=None)]
    titel: Annotated[str | None, Field(default=None)]
    undertitel: Annotated[str | None, Field(default=None)]


class Avdelning(BaseModel):
    avdelning: Annotated[list[str] | None, Field(default=None)]


# TODO: fix these models to properly parse filbilaga
# class Fil:
#     typ: Annotated[str | None, Field(default=None)]
#     namn: Annotated[str | None, Field(default=None)]
#     storlek: Annotated[str | None, Field(default=None)]
#     url: Annotated[str | None, Field(default=None)]
# class Filbilaga(BaseModel):
#     fil: Annotated[list[Fil] | None, Field(default=None)]


class CmsKategoriItem(BaseModel):
    kod: Annotated[str | None, Field(default=None)]
    namn: Annotated[str | None, Field(default=None)]


class CmsKategori(BaseModel):
    cmskategori: Annotated[list[CmsKategoriItem] | None, Field(default=None)]


class Dokument(BaseModel):
    ardometype: Annotated[str | None, Field(default=None)]
    audio: Annotated[str | None, Field(default=None)]
    avdelningar: Annotated[Avdelning | None, Field(default=None)]
    beredningsdag: Annotated[str | None, Field(default=None)]
    beslutad: Annotated[str | None, Field(default=None)]
    beslutsdag: Annotated[str | None, Field(default=None)]
    beteckning: Annotated[str | None, Field(default=None)]
    cmskategorier: Annotated[CmsKategori | None, Field(default=None)]
    database: Annotated[str | None, Field(default=None)]
    datum: Annotated[str | None, Field(default=None)]
    debatt: Annotated[str | None, Field(default=None)]
    debattdag: Annotated[str | None, Field(default=None)]
    debattgrupp: Annotated[str | None, Field(default=None)]
    debattnamn: Annotated[str | None, Field(default=None)]
    debattsekunder: Annotated[str | None, Field(default=None)]
    dok_id: Annotated[str | None, Field(default=None)]
    doktyp: Annotated[str | None, Field(default=None)]
    dokument_url_html: Annotated[str | None, Field(default=None)]
    dokument_url_text: Annotated[str | None, Field(default=None)]
    dokumentformat: Annotated[str | None, Field(default=None)]
    dokumentnamn: Annotated[str | None, Field(default=None)]
    domain: Annotated[str | None, Field(default=None)]
    id: Annotated[str | None, Field(default=None)]
    inlamnad: Annotated[str | None, Field(default=None)]
    justeringsdag: Annotated[str | None, Field(default=None)]
    kalla: Annotated[str | None, Field(default=None)]
    lang: Annotated[str | None, Field(default=None)]
    motionstid: Annotated[str | None, Field(default=None)]
    notis: Annotated[str | None, Field(default=None)]
    notisrubrik: Annotated[str | None, Field(default=None)]
    nummer: Annotated[str | None, Field(default=None)]
    organ: Annotated[str | None, Field(default=None)]
    publicerad: Annotated[str | None, Field(default=None)]
    relaterat_id: Annotated[str | None, Field(default=None)]
    relurl: Annotated[str | None, Field(default=None)]
    reservationer: Annotated[str | None, Field(default=None)]
    rm: Annotated[str | None, Field(default=None)]
    score: Annotated[str | None, Field(default=None)]
    sokdata: Annotated[SokData | None, Field(default=None)]
    status: Annotated[str | None, Field(default=None)]
    struktur: Annotated[str | None, Field(default=None)]
    subtyp: Annotated[str | None, Field(default=None)]
    summary: Annotated[str | None, Field(default=None)]
    systemdatum: Annotated[str | None, Field(default=None)]
    tempbeteckning: Annotated[str | None, Field(default=None)]
    tilldelat: Annotated[str | None, Field(default=None)]
    titel: Annotated[str | None, Field(default=None)]
    traff: Annotated[str | None, Field(default=None)]
    typ: Annotated[str | None, Field(default=None)]
    undertitel: Annotated[str | None, Field(default=None)]
    url: Annotated[str | None, Field(default=None)]
    video: Annotated[str | None, Field(default=None)]

    # TODO: remove me?
    # kall_id: Annotated[str | None, Field(default=None)]

    # TODO: remove me?
    # Is a list of intressent_ids, ignored for now
    # dokintressent: Annotated[str | None, Field(default=None)]

    # TODO: remove me?
    # Ignored filbilaga for now
    # filbilaga: Annotated[Filbilaga | None, Field(default=None)]


class DokumentLista(BaseModel):
    datum: Annotated[str | None, Field(default=None, alias="@datum")]
    dokument: Annotated[list[Dokument] | None, Field(default=None, alias="dokument")]
    ms: Annotated[str | None, Field(default=None, alias="@ms")]
    nasta_sida: Annotated[str | None, Field(default=None, alias="@nasta_sida")]
    q: Annotated[str | None, Field(default=None, alias="@q")]
    sida: Annotated[str | None, Field(default=None, alias="@sida")]
    sidor: Annotated[str | None, Field(default=None, alias="@sidor")]
    traff_fran: Annotated[str | None, Field(default=None, alias="@traff_fran")]
    traff_till: Annotated[str | None, Field(default=None, alias="@traff_till")]
    traffar: Annotated[str | None, Field(default=None, alias="@traffar")]
    varning: Annotated[str | None, Field(default=None, alias="@varning")]
    version: Annotated[str | None, Field(default=None, alias="@version")]

    class Config:
        # This will allow population by field name or alias
        allow_population_by_field_name = True


class DokumentDetaljResponse(BaseModel):
    """
    Minimal container for the single-document JSON endpoint:
    https://data.riksdagen.se/dokument/{dok_id}.json
    The schema varies somewhat by doktyp, so keep this flexible.
    """

    dokument: Annotated[dict | None, Field(default=None)]


class DokumentResponse(BaseModel):
    dokumentlista: Annotated[DokumentLista | None, Field(default=None)]
