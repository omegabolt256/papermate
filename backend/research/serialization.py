from __future__ import annotations

from dataclasses import asdict

from .models import ResearchResponse


def serialize_research_response(
    response: ResearchResponse,
) -> dict:
    return {
        "answer": response.answer,
        "sources": [
            asdict(source)
            for source in response.sources
        ],
        "evidence": [
            asdict(item)
            for item in response.evidence
        ],
        "claims": [
            asdict(claim)
            for claim in response.claims
        ],
        "citations": response.citations,
        "references": [
            asdict(reference)
            for reference in response.references
        ],
        "model_runs": [
            asdict(run)
            for run in response.model_runs
        ],
        "provenance": response.provenance,
    }