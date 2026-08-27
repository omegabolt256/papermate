from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter

from .contracts import (
    GenerationResult,
    GenerationTiming,
    IntelligenceRequest,
)


class IntelligenceProvider(ABC):
    """Provider interface used by the PaperMate intelligence gateway."""

    name: str = "unknown"

    @abstractmethod
    def generate(self, request: IntelligenceRequest) -> GenerationResult:
        raise NotImplementedError


class MockProvider(IntelligenceProvider):
    """
    Temporary provider used to prove the gateway contract.

    This deliberately does not call any AI service.
    """

    name = "mock"

    def generate(self, request: IntelligenceRequest) -> GenerationResult:
        started = perf_counter()

        text = (
            "MOCK RESPONSE: "
            f"task={request.task_type.value}"
        )

        elapsed_ms = (perf_counter() - started) * 1000

        return GenerationResult(
            text=text,
            provider=self.name,
            model="mock",
            fallback_used=False,
            timing=GenerationTiming(
                latency_ms=elapsed_ms,
            ),
            provenance={
                "task_type": request.task_type.value,
                "privacy": request.privacy.value,
                "execution": request.execution.value,
            },
        )


class IntelligenceGateway:
    """Entry point for all PaperMate model requests."""

    def __init__(self, provider: IntelligenceProvider):
        self.provider = provider

    def generate(self, request: IntelligenceRequest) -> GenerationResult:
        return self.provider.generate(request)