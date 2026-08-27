from __future__ import annotations

from .evidence import build_evidence, build_source
from .models import Evidence, ResearchRequest, Source
from backend.retrieval.searxng import SearXNGSearch


class ResearchPipeline:
    """
    Deterministic retrieval stage for PaperMate research.

    Search and evidence collection happen before model synthesis.
    """

    def __init__(
        self,
        searcher: SearXNGSearch | None = None,
    ) -> None:
        self.searcher = searcher or SearXNGSearch()

    def retrieve(
        self,
        request: ResearchRequest,
    ) -> tuple[list[Source], list[Evidence]]:

        results = self.searcher.search(
            request.question,
            limit=request.max_sources,
        )

        sources: list[Source] = []
        evidence: list[Evidence] = []

        for index, result in enumerate(results, start=1):

            # Do not allow empty search results into the
            # evidence-grounded research pipeline.
            if not result.content.strip():
                continue

            source = build_source(
                result,
                index,
            )

            item = build_evidence(
                result,
                source,
                index,
            )

            sources.append(source)
            evidence.append(item)

        return sources, evidence