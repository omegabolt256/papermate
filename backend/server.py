from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.api.research import create_research_api


app = FastAPI(
    title="PaperMate API",
    version="0.1.0",
)

research_api = create_research_api()


class ResearchRequestBody(BaseModel):
    question: str = Field(min_length=1)
    project_id: str | None = None
    max_sources: int = Field(default=10, ge=1, le=50)
    require_citations: bool = True


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "papermate",
    }


@app.post("/research")
def research(request: ResearchRequestBody) -> dict:
    try:
        return research_api.research(
            request.question,
            project_id=request.project_id,
            max_sources=request.max_sources,
            require_citations=request.require_citations,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc