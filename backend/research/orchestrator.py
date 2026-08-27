from __future__ import annotations

from backend.intelligence.providers.ollama import OllamaProvider

from .citation_renderer import render_research
from .citations import (
    CitationError,
    validate_answer_claim_coverage,
    validate_claim_citations,
)
from .models import ModelRun, ResearchRequest, ResearchResponse
from .pipeline import ResearchPipeline
from .synthesis import synthesize


class ResearchOrchestrator:
    """End-to-end evidence-grounded PaperMate research pipeline."""

    MAX_SYNTHESIS_ATTEMPTS = 3

    def __init__(
        self,
        pipeline: ResearchPipeline | None = None,
        provider: OllamaProvider | None = None,
    ) -> None:
        self.pipeline = pipeline or ResearchPipeline()
        self.provider = provider or OllamaProvider()

    def research(
        self,
        request: ResearchRequest,
    ) -> ResearchResponse:

        # 1. Discover and retrieve sources.
        sources, evidence = self.pipeline.retrieve(request)

        if not sources or not evidence:
            raise RuntimeError(
                "Research produced no usable sources or evidence."
            )

        last_error: Exception | None = None
        synthesis = None

        # 2. Synthesize and independently validate.
        #
        # Small local models can occasionally produce a claim that
        # is broader than the supplied evidence. Retry synthesis
        # rather than weakening the citation validator.
        for attempt in range(
            1,
            self.MAX_SYNTHESIS_ATTEMPTS + 1,
        ):
            try:
                synthesis = synthesize(
                    self.provider,
                    request.question,
                    sources,
                    evidence,
                )

                if request.require_citations:
                    validate_answer_claim_coverage(
                        answer=synthesis.answer,
                        claims=synthesis.claims,
                    )

                validate_claim_citations(
                    claims=synthesis.claims,
                    evidence=evidence,
                    sources=sources,
                )

                # Validation succeeded.
                break

            except CitationError as exc:
                last_error = exc

                print(
                    f"Synthesis validation failed "
                    f"(attempt {attempt}/"
                    f"{self.MAX_SYNTHESIS_ATTEMPTS}): {exc}"
                )

                synthesis = None

        if synthesis is None:
            raise RuntimeError(
                "Research synthesis failed citation validation "
                f"after {self.MAX_SYNTHESIS_ATTEMPTS} attempts."
            ) from last_error

        # 3. Build canonical citation/reference representation.
        rendered = render_research(
            answer=synthesis.answer,
            claims=synthesis.claims,
            evidence=evidence,
            sources=sources,
        )

        citations = [
            {
                "citation_id": citation.citation_id,
                "source_id": citation.source_id,
                "title": citation.title,
                "url": citation.url,
                "evidence_ids": citation.evidence_ids,
            }
            for citation in rendered.citations
        ]

        # 4. Return the validated research response.
        return ResearchResponse(
            answer=rendered.answer,
            sources=sources,
            evidence=evidence,
            claims=synthesis.claims,
            model_runs=[
                ModelRun(
                    provider="ollama",
                    model=self.provider.model,
                    fallback_used=False,
                )
            ],
            provenance={
                "task": "research",
                "pipeline": [
                    "searxng",
                    "evidence",
                    "ollama",
                    "claim_validation",
                    "citation_rendering",
                ],
                "citation_validation": "passed",
            },
            citations=citations,
            references=rendered.references,
        )