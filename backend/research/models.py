from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ResearchRequest:
    question: str
    project_id: str | None = None
    max_sources: int = 10
    require_citations: bool = True


@dataclass
class Source:
    source_id: str
    title: str
    url: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    source_type: str = "unknown"


@dataclass
class Evidence:
    evidence_id: str
    source_id: str
    content: str
    location: str | None = None
    page: int | None = None
    quote: str | None = None


@dataclass
class Claim:
    claim_id: str
    text: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class ModelRun:
    provider: str
    model: str
    fallback_used: bool
    timestamp: str = field(default_factory=utc_now)

@dataclass
class ResearchResponse:
    answer: str
    sources: list[Source] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    model_runs: list[ModelRun] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    citations: list[dict[str, Any]] = field(default_factory=list)
    references: list[Source] = field(default_factory=list)