from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MemoryResult:
    content: str
    score: float | None = None
    metadata: dict[str, Any] | None = None


class MemPalaceTool:
    """
    PaperMate -> MemPalace MCP adapter.

    PaperMate remains completely independent from Sage.
    """

    def __init__(
        self,
        palace_path: str = r"D:\Projects\PaperMate\data\memory",
    ) -> None:
        self.palace_path = palace_path

    async def _call_mcp_async(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:

        server = StdioServerParameters(
            command="mempalace-mcp",
            args=[
                "--palace",
                self.palace_path,
            ],
        )

        async with stdio_client(server) as streams:
            async with ClientSession(
                streams[0],
                streams[1],
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                return result

    def _call_mcp(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        return asyncio.run(
            self._call_mcp_async(
                tool_name,
                arguments,
            )
        )

    def search(
        self,
        query: str,
        *,
        wing: str | None = None,
        room: str | None = None,
        limit: int = 5,
        max_distance: float = 1.5,
    ) -> list[MemoryResult]:

        arguments: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "max_distance": max_distance,
        }

        if wing:
            arguments["wing"] = wing

        if room:
            arguments["room"] = room

        result = self._call_mcp(
            "mempalace_search",
            arguments,
        )

        if not result.content:
            return []

        import json

        data = json.loads(
            result.content[0].text
        )

        return [
            MemoryResult(
                content=item.get("text", ""),
                score=item.get("similarity"),
                metadata={
                    "drawer_id": item.get("drawer_id"),
                    "wing": item.get("wing"),
                    "room": item.get("room"),
                    "source_file": item.get("source_file"),
                    "source_path": item.get("source_path"),
                    "created_at": item.get("created_at"),
                },
            )
            for item in data.get("results", [])
        ]

    def store(
        self,
        content: str,
        *,
        wing: str,
        room: str = "general",
        source_file: str | None = None,
        added_by: str = "papermate",
    ) -> Any:

        arguments: dict[str, Any] = {
            "wing": wing,
            "room": room,
            "content": content,
            "added_by": added_by,
        }

        if source_file:
            arguments["source_file"] = source_file

        return self._call_mcp(
            "mempalace_add_drawer",
            arguments,
        )

    def knowledge_graph(
        self,
        entity: str,
        *,
        direction: str = "both",
        as_of: str | None = None,
    ) -> Any:

        arguments: dict[str, Any] = {
            "entity": entity,
            "direction": direction,
        }

        if as_of:
            arguments["as_of"] = as_of

        return self._call_mcp(
            "mempalace_kg_query",
            arguments,
        )