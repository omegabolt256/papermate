from __future__ import annotations

import os

import requests

from .search import ResearchSearcher, SearchResult


class SearXNGResearchSearcher(ResearchSearcher):
    """PaperMate searcher backed by SearXNG."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 10,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv(
                "PAPERMATE_SEARXNG_URL",
                "http://127.0.0.1:8080",
            )
        ).rstrip("/")

        self.timeout = timeout

    def search(
        self,
        question: str,
        *,
        max_results: int = 10,
    ) -> list[SearchResult]:

        response = requests.get(
            f"{self.base_url}/search",
            params={
                "q": question,
                "format": "json",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        results: list[SearchResult] = []

        for index, item in enumerate(
            data.get("results", [])[:max_results],
            start=1,
        ):
            url = item.get("url")

            if not url:
                continue

            results.append(
                SearchResult(
                    source_id=f"WEB-{index:03d}",
                    title=item.get("title", "Untitled"),
                    url=url,
                    snippet=item.get("content", ""),
                    authors=(
                        [item["author"]]
                        if item.get("author")
                        else []
                    ),
                    source_type="web",
                )
            )

        return results