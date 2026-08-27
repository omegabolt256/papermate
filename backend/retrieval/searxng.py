from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class SearchResult:
    title: str
    url: str
    content: str = ""
    engine: str | None = None
    score: float | None = None


class SearXNGSearch:
    """PaperMate adapter for a local SearXNG instance."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SearchResult]:

        response = requests.get(
            f"{self.base_url}/search",
            params={
                "q": query,
                "format": "json",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data: dict[str, Any] = response.json()

        results: list[SearchResult] = []

        for item in data.get("results", [])[:limit]:
            url = item.get("url")

            if not url:
                continue

            results.append(
                SearchResult(
                    title=str(item.get("title", "")),
                    url=str(url),
                    content=str(item.get("content", "")),
                    engine=item.get("engine"),
                    score=item.get("score"),
                )
            )

        return results