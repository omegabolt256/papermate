from __future__ import annotations

from .mock_search import MockResearchSearcher
from .retrieval import ResearchRetriever, RetrievedSource
from .search import SearchResult


class MockResearchRetriever(ResearchRetriever):
    """Deterministic source retrieval for pipeline tests."""

    def retrieve(
        self,
        source: SearchResult,
    ) -> RetrievedSource:

        return RetrievedSource(
            source=source,
            content=(
                "Randomized controlled trials are commonly used "
                "to evaluate interventions. This is deterministic "
                "test evidence."
            ),
        )