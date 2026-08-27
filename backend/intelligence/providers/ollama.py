from __future__ import annotations

from typing import Any

import requests

from backend.intelligence.providers.base import IntelligenceProvider


class OllamaProvider(IntelligenceProvider):
    """PaperMate provider for a local Ollama instance."""

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 160,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 600,
        **kwargs: Any,
    ) -> str:

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise RuntimeError(
                f"Unexpected Ollama response: {data}"
            )

        return str(data["response"])