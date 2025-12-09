from __future__ import annotations

from typing import List, Optional

import httpx
from numpy.ma.extras import unique

from app.config import settings
from app.services.paper_search.clients import get_unpaywall_oa_info
from app.services.paper_search.models import ResolvedPDF, OALocation, UnpaywallOAInfo

def _collect_candidate_urls(oa_info: UnpaywallOAInfo) -> List[tuple[str, str]]:
    candidates: List[tuple[str, str]] = []

    if oa_info.best_oa_location:
        loc = oa_info.best_oa_location
        if loc.pdf_url:
            candidates.append((loc.pdf_url, "unpaywall_best"))
        if loc.url and loc.url != loc.pdf_url:
            candidates.append((loc.url, "unpaywall_best"))

    for loc in oa_info.oa_locations:
        if loc.pdf_url:
            candidates.append((loc.pdf_url, "unpaywall_alt"))
        if loc.url and loc.url != loc.pdf_url:
            candidates.append((loc.url, "unpaywall_alt"))

    # De-duplicate
    seen = set()
    unique: List[tuple[str, str]] = []
    for url, tag in candidates:
        if url not in seen:
            seen.add(url)
            unique.append((url, tag))

    return unique

def _looks_like_pdf(content_type: Optional[str], url: str) -> bool:
    if content_type and "application/pdf" in content_type.lower():
        return True
    if url.lower().endswith(".pdf"):
        return True
    return False

def resolve_pdf_for_doi(doi: str) -> Optional[ResolvedPDF]:
    oa_info = get_unpaywall_oa_info(doi)
    if not oa_info:
        return None

    candidates = _collect_candidate_urls(oa_info)
    if not candidates:
        return None

    with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS, follow_redirects=True) as client:
        for url, tag in candidates:
            try:
                try:
                    # HEAD
                    head_resp = client.head(url)
                    if head_resp.status_code == 405:
                        raise httpx.HTTPError("HEAD not allowed")
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get("Content-Type")
                    if _looks_like_pdf(content_type, url):
                        return ResolvedPDF(doi=doi, url=str(head_resp.url), source=tag)
                except httpx.HTTPError:
                    # GET
                    try:
                        with client.stream("GET", url) as get_resp:
                            get_resp.raise_for_status()
                            content_type = get_resp.headers.get("Content-Type")
                            if _looks_like_pdf(content_type, str(get_resp.url)):
                                return ResolvedPDF(
                                    doi=doi,
                                    url=str(get_resp.url),
                                    source=tag
                                )
                    except httpx.HTTPError:
                        continue

            except httpx.HTTPError:
                continue

    return None

