from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    source_id: str
    title: str
    url: str | None = None
    snippet: str = ""
    authors: list[str] | None = None
    year: int | None = None
    source_type: str = "web"


class ResearchSearcher(ABC):
    """Source-discovery contract for PaperMate research."""

    @abstractmethod
    def search(
        self,
        question: str,
        *,
        max_results: int = 10,
    ) -> list[SearchResult]:
        raise NotImplementedError