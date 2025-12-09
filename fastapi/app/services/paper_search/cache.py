from __future__ import annotations

import json
from typing import List, Optional

import redis

from app.config import settings
from app.services.paper_search.models import SearchResult

_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL)
    return _redis_client

def _normalise_query(q: str) -> str:
    return " ".join(q.strip().lower().split())

def get_cached_search(query: str) -> Optional[List[SearchResult]]:
    r = get_redis_client()
    key = f"fpapers:search:{_normalise_query()}"
    raw = r.get(key)
    if raw is None:
        return None
    try:
        data = json.loads(raw)
        return [SearchResult.model_validate(item) for item in data]
    except Exception:
        return None

def set_cached_search(query: str, results: List[SearchResult], ttl_seconds: int = 6*60*60) -> None:
    r = get_redis_client()
    key = f"papers:search:{_normalise_query(query)}"
    payload = [res.model_dump() for res in results]
    r.setex(key, ttl_seconds, json.dumps(payload))

def get_cached_pdf_url(doi: str) -> Optional[str]:
    r = get_redis_client()
    key = f"papers:doi:{doi}:pdf_url"
    raw = r.get(key)
    if raw is None:
        return None
    return raw.decode("utf-8")

def set_cached_pdf_url(doi: str, url: str, ttl_seconds: int = 6*60*60) -> None:
    r = get_redis_client()
    key = f"papers:doi:{doi}:pdf_url"
    r.setex(key, ttl_seconds, url)

