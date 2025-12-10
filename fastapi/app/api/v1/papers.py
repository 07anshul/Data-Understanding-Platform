from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import httpx

from app.services.paper_search.clients import search_crossref, get_unpaywall_oa_info
from app.services.paper_search.models import SearchResult
from app.services.paper_search.resolver import resolve_pdf_for_doi
from app.services.paper_search.cache import get_cached_search, set_cached_search, get_cached_pdf_url, set_cached_pdf_url

router = APIRouter(prefix="/papers", tags=["papers"])

@router.get("/search", response_model=List[SearchResult])
def search_papers(
        query: str = Query(..., min_length=3, max_length=300),
        limit: int = Query(10, ge=1, le=100),
):
    # search cache
    cached = get_cached_search(query)
    if cached is not None:
        return cached[:limit]

    # external search
    try:
        metas = search_crossref(query=query, limit=limit)
    except Exception:
        # log the exception
        raise HTTPException(status_code=502, detail="Upstream search failed")

    results: List[SearchResult] = []

    for meta in metas:
        pdf_available = False
        pdf_source = "none"

        if meta.doi:
            oa_info = get_unpaywall_oa_info(meta.doi)
            if oa_info and oa_info.best_oa_location and (
                oa_info.best_oa_location.pdf_url or oa_info.best_oa_location.url
            ):
                pdf_available = True
                pdf_source = "unpaywall"

        results.append(SearchResult(
            title=meta.title,
            doi=meta.doi,
            year=meta.year,
            authors=meta.authors,
            pdf_available=pdf_available,
            pdf_source=pdf_source
        ))

    # store cache
    set_cached_search(query, results)

    return results

def _pdf_stream(url: str, chunk_size: int = 1024*1024):
    with httpx.stream("GET", url, timeout=30.0, follow_redirects=True) as resp:
        resp.raise_for_status()
        for chunk in resp.iter_bytes(chunk_size):
            if not chunk:
                break
            yield chunk

@router.get("/download")
def download_paper(doi: str):
    if not doi:
        raise HTTPException(status_code=400, detail="DOI is required")

    # check cache
    cached_url = get_cached_pdf_url(doi)
    url_to_use: Optional[str] = cached_url

    if url_to_use is None:
        resolved = resolve_pdf_for_doi(doi)
        if not resolved:
            raise HTTPException(status_code=404, detail="No OA PDF found for this DOI")
        url_to_use = resolved.url
        # cache url
        set_cached_pdf_url(doi, url_to_use)

    safe_doi = doi.replace("/", "_")
    filename = f"{safe_doi}.pdf"

    try:
        return StreamingResponse(
            _pdf_stream(url_to_use),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    except httpx.HTTPError:
        # delete cache if needed - later priority
        raise HTTPException(status_code=502, detail="Failed to download PDF from source")
