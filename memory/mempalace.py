from __future__ import annotations

from typing import Any

from mcp import ClientSession, StdioServerParameters, stdio_client

from .contracts import (
    MemoryProvider,
    MemoryRecord,
    MemoryScope,
)


class MemPalaceProvider(MemoryProvider):
    """PaperMate's native adapter for MemPalace MCP."""

    def __init__(
        self,
        *,
        palace: str | None = None,
        wing: str = "papermate",
        room: str = "general",
    ):
        self.palace = palace
        self.wing = wing
        self.room = room

    def _server(self) -> StdioServerParameters:
        args: list[str] = []

        if self.palace:
            args.extend(["--palace", self.palace])

        return StdioServerParameters(
            command="mempalace-mcp",
            args=args,
        )

    async def _call_async(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:

        async with stdio_client(self._server()) as streams:
            read_stream, write_stream = streams

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                return self._extract_result(result)

    def _call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        import asyncio

        return asyncio.run(
            self._call_async(
                tool_name,
                arguments,
            )
        )

    @staticmethod
    def _extract_result(response: Any) -> Any:
        structured = getattr(
            response,
            "structured_content",
            None,
        )

        if structured is not None:
            return structured

        content = getattr(
            response,
            "content",
            None,
        )

        if content:
            values = []

            for item in content:
                text = getattr(item, "text", None)

                if text is not None:
                    values.append(text)

            if len(values) == 1:
                return values[0]

            if values:
                return values

        return response

    @staticmethod
    def _scope_room(
        scope: MemoryScope,
        project_id: str | None,
        paper_id: str | None,
        research_question_id: str | None,
    ) -> tuple[str, str]:

        if scope == MemoryScope.USER:
            return "user", "general"

        if scope == MemoryScope.PROJECT:
            return (
                project_id or "papermate",
                "general",
            )

        if scope == MemoryScope.PAPER:
            return (
                project_id or "papermate",
                f"paper:{paper_id or 'unknown'}",
            )

        if scope == MemoryScope.RESEARCH_QUESTION:
            return (
                project_id or "papermate",
                f"question:{research_question_id or 'unknown'}",
            )

        if scope == MemoryScope.SESSION:
            return (
                project_id or "papermate",
                "session",
            )

        return "papermate", "general"

    def search(
        self,
        query: str,
        *,
        scope: MemoryScope | None = None,
        project_id: str | None = None,
        limit: int = 5,
    ) -> list[MemoryRecord]:

        if not query.strip():
            raise ValueError(
                "Memory search query cannot be empty."
            )

        wing = None
        room = None

        if scope is not None:
            wing, room = self._scope_room(
                scope,
                project_id,
                None,
                None,
            )
        elif project_id:
            wing = project_id

        result = self._call(
            "mempalace_search",
            {
                "query": query.strip()[:250],
                "limit": max(1, min(limit, 100)),
                **({"wing": wing} if wing else {}),
                **({"room": room} if room else {}),
            },
        )

        if isinstance(result, dict):
            result = (
                result.get("results")
                or result.get("drawers")
                or result.get("items")
                or []
            )

        if not isinstance(result, list):
            return []

        records: list[MemoryRecord] = []

        for item in result:
            if not isinstance(item, dict):
                continue

            content = (
                item.get("content")
                or item.get("text")
                or ""
            )

            if not content:
                continue

            records.append(
                MemoryRecord(
                    content=str(content),
                    scope=scope or MemoryScope.PROJECT,
                    project_id=project_id,
                    memory_id=(
                        item.get("id")
                        or item.get("drawer_id")
                    ),
                    score=item.get("score")
                    or item.get("similarity"),
                    metadata=item,
                )
            )

        return records

    def remember(
        self,
        memory: MemoryRecord,
    ) -> MemoryRecord:

        if not memory.content.strip():
            raise ValueError(
                "Memory content cannot be empty."
            )

        wing, room = self._scope_room(
            memory.scope,
            memory.project_id,
            memory.paper_id,
            memory.research_question_id,
        )

        source_file = None

        if memory.metadata:
            source_file = memory.metadata.get(
                "source_file"
            )

        result = self._call(
            "mempalace_add_drawer",
            {
                "wing": wing,
                "room": room,
                "content": memory.content.strip(),
                **(
                    {"source_file": source_file}
                    if source_file
                    else {}
                ),
                "added_by": "papermate",
            },
        )

        if isinstance(result, dict):
            memory_id = (
                result.get("id")
                or result.get("drawer_id")
            )
        else:
            memory_id = None

        return MemoryRecord(
            content=memory.content.strip(),
            scope=memory.scope,
            project_id=memory.project_id,
            paper_id=memory.paper_id,
            research_question_id=memory.research_question_id,
            memory_id=memory_id,
            metadata=memory.metadata,
        )

    def update(
        self,
        memory_id: str,
        content: str,
    ) -> MemoryRecord:

        if not memory_id.strip():
            raise ValueError(
                "memory_id cannot be empty."
            )

        if not content.strip():
            raise ValueError(
                "Memory content cannot be empty."
            )

        self._call(
            "mempalace_update_drawer",
            {
                "drawer_id": memory_id,
                "content": content.strip(),
            },
        )

        return MemoryRecord(
            content=content.strip(),
            scope=MemoryScope.PROJECT,
            memory_id=memory_id,
        )

    def forget(
        self,
        memory_id: str,
    ) -> None:

        if not memory_id.strip():
            raise ValueError(
                "memory_id cannot be empty."
            )

        self._call(
            "mempalace_delete_drawer",
            {
                "drawer_id": memory_id,
            },
        )