from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MemoryScope(str, Enum):
    USER = "user"
    PROJECT = "project"
    PAPER = "paper"
    RESEARCH_QUESTION = "research_question"
    SESSION = "session"


@dataclass(frozen=True)
class MemoryRecord:
    content: str
    scope: MemoryScope

    project_id: str | None = None
    paper_id: str | None = None
    research_question_id: str | None = None

    memory_id: str | None = None
    score: float | None = None

    metadata: dict[str, Any] | None = None


class MemoryProvider(ABC):
    """Long-term memory interface for PaperMate."""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        scope: MemoryScope | None = None,
        project_id: str | None = None,
        limit: int = 5,
    ) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    def remember(
        self,
        memory: MemoryRecord,
    ) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        memory_id: str,
        content: str,
    ) -> MemoryRecord:
        raise NotImplementedError

    @abstractmethod
    def forget(
        self,
        memory_id: str,
    ) -> None:
        raise NotImplementedError