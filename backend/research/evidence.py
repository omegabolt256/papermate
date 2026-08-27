from __future__ import annotations

from .models import Evidence, Source
from backend.retrieval.searxng import SearchResult


def build_source(result: SearchResult, index: int) -> Source:
    return Source(
        source_id=f"SRC-{index:03d}",
        title=result.title,
        url=result.url,
        source_type="web",
    )


def build_evidence(
    result: SearchResult,
    source: Source,
    index: int,
) -> Evidence:
    return Evidence(
        evidence_id=f"EVD-{index:03d}",
        source_id=source.source_id,
        content=result.content,
    )