from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel

class PaperMetaData(BaseModel):
    title: str
    doi: Optional[str]
    year: Optional[int]
    authors: List[str]

class SearchResult(BaseModel):
    title: str
    doi: Optional[str]
    year: Optional[int]
    authors: List[str]
    pdf_available: bool
    pdf_source: Optional[Literal["unpaywall", "none"]] = "none"

class OALocation(BaseModel):
    pdf_url: Optional[str] = None
    url: Optional[str] = None
    host_type: Optional[str] = None

class UnpaywallOAInfo(BaseModel):
    best_oa_location: Optional[OALocation] = None
    oa_locations: List[OALocation] = []

