from __future__ import annotations

import re
from dataclasses import dataclass


_URL_RE = re.compile(r"https?://\S+")
_DOI_RE = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
    re.I,
)


@dataclass(frozen=True)
class CompressionBudget:
    max_context_chars: int = 14000
    max_tool_chars: int = 12000
    max_message_chars: int = 3000
    max_history_messages: int = 6
    max_evidence_items: int = 10
    max_evidence_chars: int = 12000


class ContextCompressor:
    """Deterministic context reduction for PaperMate."""

    def __init__(
        self,
        budget: CompressionBudget | None = None,
    ) -> None:
        self.budget = budget or CompressionBudget()

    @staticmethod
    def _identifiers(text: str) -> list[str]:
        return list(
            dict.fromkeys(
                _URL_RE.findall(text) + _DOI_RE.findall(text)
            )
        )

    def trim(self, text: str, limit: int) -> str:
        text = str(text)

        if len(text) <= limit:
            return text

        identifiers = self._identifiers(text)

        marker = "\n...[CONTEXT COMPRESSED]...\n"

        # Reserve space for important research identifiers.
        reserved = ""

        for identifier in identifiers:
            candidate = reserved + "\n" + identifier

            if len(candidate) + len(marker) <= limit:
                reserved = candidate

        body_budget = limit - len(reserved) - len(marker)

        if body_budget <= 0:
            return reserved[:limit]

        head = body_budget // 2
        tail = body_budget - head

        body = (
            text[:head]
            + marker
            + text[-tail:]
        )

        return body + reserved

    def compress_messages(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        if not messages:
            return []

        recent = messages[
            -self.budget.max_history_messages:
        ]

        output: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        for message in recent:
            role = str(
                message.get("role", "user")
            )

            content = self.trim(
                str(message.get("content", "")),
                self.budget.max_message_chars,
            )

            key = (
                role,
                content.strip().lower(),
            )

            if key in seen:
                continue

            seen.add(key)

            output.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        return output

    def compress_evidence(
        self,
        evidence: list[dict],
    ) -> str:
        if not evidence:
            return ""

        selected = evidence[
            : self.budget.max_evidence_items
        ]

        blocks: list[str] = []

        for index, item in enumerate(
            selected,
            1,
        ):
            if not isinstance(item, dict):
                continue

            title = str(
                item.get("title", "")
            ).strip()

            url = str(
                item.get("url", "")
            ).strip()

            content = str(
                item.get("content")
                or item.get("snippet")
                or item.get("abstract")
                or ""
            ).strip()

            blocks.append(
                f"[SOURCE {index}]\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}\n"
                f"[END SOURCE {index}]"
            )

        return self.trim(
            "\n\n".join(blocks),
            self.budget.max_evidence_chars,
        )

    def compress_tool_result(
        self,
        result: object,
    ) -> str:
        return self.trim(
            str(result),
            self.budget.max_tool_chars,
        )

    def compress_context(
        self,
        text: str,
    ) -> str:
        return self.trim(
            text,
            self.budget.max_context_chars,
        )