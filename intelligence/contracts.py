from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    CHAT = "chat"
    EXTRACT = "extract"
    SUMMARIZE = "summarize"
    SYNTHESIZE = "synthesize"
    CRITIQUE = "critique"
    TOOL = "tool"


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    STRICT = "strict"


class ExecutionProfile(str, Enum):
    REALTIME = "realtime"
    STANDARD = "standard"
    BATCH = "batch"
    BACKGROUND = "background"


@dataclass(frozen=True)
class IntelligenceRequest:
    messages: list[dict[str, str]]
    task_type: TaskType = TaskType.CHAT

    privacy: PrivacyLevel = PrivacyLevel.PUBLIC
    execution: ExecutionProfile = ExecutionProfile.STANDARD

    required_context_tokens: int = 0
    requires_structured_output: bool = False
    response_schema: dict[str, Any] | None = None

    model: str | None = None
    temperature: float = 0.3
    max_tokens: int = 600

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(frozen=True)
class GenerationTiming:
    latency_ms: float | None = None


@dataclass(frozen=True)
class GenerationResult:
    text: str

    provider: str
    model: str

    fallback_used: bool = False

    usage: GenerationUsage = field(default_factory=GenerationUsage)
    timing: GenerationTiming = field(default_factory=GenerationTiming)

    provenance: dict[str, Any] = field(default_factory=dict)