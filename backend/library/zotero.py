from __future__ import annotations

import re
from typing import Any

import httpx


class ZoteroConnectionError(RuntimeError):
    """Zotero local API could not be reached or returned an error."""


def normalize_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a Zotero API item into PaperMate index metadata."""
    data = item.get("data", {})
    item_type = data.get("itemType", "")

    if not data or item_type in {"attachment", "note", "annotation"}:
        return None

    date = data.get("date", "")
    match = re.search(r"\b(?:19|20)\d{2}\b", date)
    year = int(match.group()) if match else None

    creators = []
    for creator in data.get("creators", []):
        name = creator.get("name")
        if not name:
            name = " ".join(
                part for part in (
                    creator.get("firstName", ""),
                    creator.get("lastName", ""),
                ) if part
            )
        if name:
            creators.append(name)

    return {
        "zotero_key": item.get("key", data.get("key", "")),
        "title": data.get("title", "").strip(),
        "creators": "; ".join(creators),
        "year": year,
        "doi": data.get("DOI") or None,
        "item_type": item_type,
        "zotero_url": data.get("url") or None,
        "date_added": data.get("dateAdded") or None,
        "date_modified": data.get("dateModified") or None,
    }


class ZoteroLocalClient:
    """Read-only client for Zotero's local API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:23119",
        timeout: float = 10.0,
        page_size: int = 100,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.page_size = max(1, min(page_size, 100))

    def fetch_raw_items(self) -> list[dict[str, Any]]:
        """Fetch all Zotero items, including attachments, without modifying Zotero."""
        items: list[dict[str, Any]] = []
        start = 0

        try:
            with httpx.Client(
                timeout=self.timeout,
                trust_env=False,
                headers={"Zotero-API-Version": "3"},
            ) as client:
                while True:
                    response = client.get(
                        f"{self.base_url}/api/users/0/items",
                        params={
                            "format": "json",
                            "limit": self.page_size,
                            "start": start,
                        },
                    )
                    response.raise_for_status()
                    batch = response.json()

                    if not isinstance(batch, list):
                        raise ZoteroConnectionError(
                            "Zotero returned an unexpected response format."
                        )

                    items.extend(batch)
                    if len(batch) < self.page_size:
                        break
                    start += len(batch)

        except ZoteroConnectionError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise ZoteroConnectionError(
                "Could not read Zotero's local API. Confirm Zotero is running "
                "and its local API is accessible, then retry."
            ) from exc

        return items

    def fetch_items(self) -> list[dict[str, Any]]:
        """Fetch and normalize bibliographic records for PaperMate's index."""
        items = self.fetch_raw_items()

        papers = []
        for item in items:
            paper = normalize_item(item)
            if paper and paper["zotero_key"] and paper["title"]:
                papers.append(paper)

        return papers
