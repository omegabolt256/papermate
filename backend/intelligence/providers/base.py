from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IntelligenceProvider(ABC):
    """Provider contract used by the PaperMate intelligence gateway."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 600,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError