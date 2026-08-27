from __future__ import annotations

from dataclasses import dataclass

from backend.research.models import ResearchRequest
from backend.research.orchestrator import ResearchOrchestrator
from backend.research.serialization import serialize_research_response


@dataclass
class ResearchAPI:
    orchestrator: ResearchOrchestrator

    def research(
        self,
        question: str,
        *,
        project_id: str | None = None,
        max_sources: int = 10,
        require_citations: bool = True,
    ) -> dict:
        request = ResearchRequest(
            question=question,
            project_id=project_id,
            max_sources=max_sources,
            require_citations=require_citations,
        )

        response = self.orchestrator.research(request)

        return serialize_research_response(response)


def create_research_api() -> ResearchAPI:
    return ResearchAPI(
        orchestrator=ResearchOrchestrator(),
    )