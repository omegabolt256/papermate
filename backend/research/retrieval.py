from __future__ import annotations

from abc import ABC, abstractmethod

from .search import SearchResult


class RetrievedSource:
    def __init__(
        self,
        source: SearchResult,
        content: str,
    ) -> None:
        self.source = source
        self.content = content


class ResearchRetriever(ABC):
    """Retrieves source content from discovered research sources."""

    @abstractmethod
    def retrieve(
        self,
        source: SearchResult,
    ) -> RetrievedSource:
        raise NotImplementedError