from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.intelligence.context_compressor import ContextCompressor
from backend.intelligence.providers.base import IntelligenceProvider
from backend.tools.memory import MemPalaceTool


@dataclass
class IntelligenceRequest:
    task_type: str
    prompt: str
    project_id: str | None = None
    system: str | None = None
    temperature: float = 0.3
    max_tokens: int = 600
    use_memory: bool = True


@dataclass
class IntelligenceResponse:
    text: str
    provider: str
    model: str
    memory_used: bool
    memory_results: int
    provenance: dict[str, Any] = field(default_factory=dict)


class IntelligenceGateway:
    """
    PaperMate intelligence orchestration boundary.

    The gateway coordinates memory, context compression, and inference.
    It does not implement any of those systems itself.
    """

    def __init__(
        self,
        provider: IntelligenceProvider,
        *,
        provider_name: str,
        model_name: str,
        memory: MemPalaceTool | None = None,
        compressor: ContextCompressor | None = None,
    ) -> None:
        self.provider = provider
        self.provider_name = provider_name
        self.model_name = model_name
        self.memory = memory or MemPalaceTool()
        self.compressor = compressor or ContextCompressor()

    def generate(
        self,
        request: IntelligenceRequest,
    ) -> IntelligenceResponse:

        memory_results = []

        if request.use_memory:
            memory_results = self.memory.search(
                request.prompt,
                wing=request.project_id,
                limit=5,
            )

        memory_context = ""

        if memory_results:
            evidence = [
                {
                    "title": "PaperMate long-term memory",
                    "content": result.content,
                    "source_file": (
                        result.metadata or {}
                    ).get("source_file", ""),
                }
                for result in memory_results
            ]

            memory_context = self.compressor.compress_evidence(
                evidence
            )

        prompt = request.prompt

        if memory_context:
            prompt = (
                "RELEVANT LONG-TERM MEMORY:\n"
                f"{memory_context}\n\n"
                "CURRENT REQUEST:\n"
                f"{request.prompt}"
            )

        text = self.provider.generate(
            prompt,
            system=request.system,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return IntelligenceResponse(
            text=text,
            provider=self.provider_name,
            model=self.model_name,
            memory_used=bool(memory_results),
            memory_results=len(memory_results),
            provenance={
                "task_type": request.task_type,
                "project_id": request.project_id,
                "memory_used": bool(memory_results),
                "memory_results": len(memory_results),
                "context_compressed": bool(memory_context),
            },
        )