from __future__ import annotations

from .search import ResearchSearcher, SearchResult


class MockResearchSearcher(ResearchSearcher):
    """Deterministic searcher used for pipeline tests."""

    def search(
        self,
        question: str,
        *,
        max_results: int = 10,
    ) -> list[SearchResult]:

        return [
            SearchResult(
                source_id="SRC-001",
                title="Controlled Trial Methodology",
                url="https://example.org/trial-methodology",
                snippet=(
                    "Randomized controlled trials are commonly used "
                    "to evaluate interventions."
                ),
                authors=["Example Author"],
                year=2026,
                source_type="test",
            )
        ][:max_results]