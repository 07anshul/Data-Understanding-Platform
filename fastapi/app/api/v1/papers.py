from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.services.paper_search.clients import search_crossref, get_unpaywall_oa_info
from app.services.paper_search.models import SearchResult

router = APIRouter(prefix="/papers", tags=["papers"])

@router.get("/search", response_model=List[SearchResult])
def search_papers(
        query: str = Query(..., min_length=3, max_length=300),
        limit: int = Query(10, ge=1, le=25),
):
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

    return results