from __future__ import annotations

from typing import List, Optional

import httpx

from app.config import settings
from app.services.paper_search.models import PaperMetaData, UnpaywallOAInfo

def search_crossref(query: str, limit: int=10) -> List[PaperMetaData]:
    params = {"query": query, "rows": limit}

    with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
        resp = client.get(settings.CROSSREF_BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    items = data.get("message", {}).get("items", [])
    results: List[PaperMetaData] = []

    for item in items:
        title_list = item.get("title") or []
        title = title_list[0] if title_list else "Untitled"

        doi = item.get("DOI")
        year = None
        for field in ("published-print", "published-online", "issued"):
            if field in item:
                parts = item[field].get("date-parts", [])
                if parts and parts[0]:
                    year = parts[0][0]
                    break

        authors_raw = item.get("authors") or []
        authors = []
        for a in authors_raw:
            given = a.get("given") or ""
            family = a.get("family") or ""
            full = " ".join(x for x in [given, family] if x).strip()
            if full:
                authors.append(full)

        results.append(
            PaperMetaData(
                title=title,
                doi=doi,
                year=year,
                authors=authors
            )
        )

    return results

def get_unpaywall_oa_info(doi: str) -> Optional[UnpaywallOAInfo]:
    if not doi:
        return

    url = f"{settings.UNPAYWALL_BASE_URL}/{doi}"
    params = {"email": settings.UNPAYWALL_EMAIL}

    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return None

    if not data.get("is_oa"):
        return None

    return UnpaywallOAInfo(
        best_oa_location=data.get("best_oa_location"),
        oa_locations=data.get("oa_locations") or [],
    )