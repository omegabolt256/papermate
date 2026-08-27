from __future__ import annotations

from dataclasses import dataclass

from .models import Claim, Evidence, Source


@dataclass
class RenderedCitation:
    citation_id: str
    source_id: str
    title: str
    url: str | None
    evidence_ids: list[str]


@dataclass
class RenderedResearch:
    answer: str
    citations: list[RenderedCitation]
    references: list[Source]
    claims: list[Claim]
    evidence: list[Evidence]


def render_research(
    answer: str,
    claims: list[Claim],
    evidence: list[Evidence],
    sources: list[Source],
) -> RenderedResearch:
    source_map = {
        source.source_id: source
        for source in sources
    }

    evidence_map = {
        item.evidence_id: item
        for item in evidence
    }

    citations: list[RenderedCitation] = []
    seen_sources: set[str] = set()

    for claim in claims:
        for evidence_id in claim.evidence_ids:
            item = evidence_map.get(evidence_id)

            if item is None:
                continue

            source = source_map.get(item.source_id)

            if source is None:
                continue

            if source.source_id in seen_sources:
                continue

            seen_sources.add(source.source_id)

            citations.append(
                RenderedCitation(
                    citation_id=f"REF-{len(citations) + 1:03d}",
                    source_id=source.source_id,
                    title=source.title,
                    url=source.url,
                    evidence_ids=[
                        evidence_item.evidence_id
                        for evidence_item in evidence
                        if evidence_item.source_id == source.source_id
                    ],
                )
            )

    return RenderedResearch(
        answer=answer,
        citations=citations,
        references=[
            source
            for source in sources
            if source.source_id in seen_sources
        ],
        claims=claims,
        evidence=evidence,
    )