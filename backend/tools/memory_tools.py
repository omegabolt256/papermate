from __future__ import annotations

from typing import Any

from backend.tools.memory import MemPalaceTool
from backend.tools.registry import ToolRegistry


def register_memory_tools(
    registry: ToolRegistry,
    memory: MemPalaceTool | None = None,
) -> None:
    """Register PaperMate's long-term memory capabilities."""

    memory = memory or MemPalaceTool()

    registry.register(
        name="memory_search",
        description=(
            "Search PaperMate's long-term research memory "
            "using semantic retrieval."
        ),
        handler=memory.search,
    )

    registry.register(
        name="memory_store",
        description=(
            "Store durable research/project information "
            "in PaperMate's long-term memory."
        ),
        handler=memory.store,
    )

    registry.register(
        name="knowledge_graph",
        description=(
            "Query structured relationships and temporally "
            "valid facts from PaperMate's long-term memory."
        ),
        handler=memory.knowledge_graph,
    )