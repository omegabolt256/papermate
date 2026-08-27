from __future__ import annotations

from time import perf_counter

import httpx

from ..contracts import (
    GenerationResult,
    GenerationTiming,
    IntelligenceRequest,
)
from ..gateway import IntelligenceProvider


class OllamaProvider(IntelligenceProvider):
    """PaperMate v2 provider for a local Ollama instance."""

    name = "ollama"

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 180.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        request: IntelligenceRequest,
    ) -> GenerationResult:

        started = perf_counter()

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": request.messages,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens,
                    },
                },
            )

        response.raise_for_status()

        data = response.json()

        try:
            text = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Ollama response: {data}"
            ) from exc

        elapsed_ms = (perf_counter() - started) * 1000

        return GenerationResult(
            text=text,
            provider=self.name,
            model=self.model,
            fallback_used=False,
            timing=GenerationTiming(
                latency_ms=elapsed_ms,
            ),
            provenance={
                "backend": "ollama",
                "base_url": self.base_url,
            },
        )