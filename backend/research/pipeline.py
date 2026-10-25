from __future__ import annotations

import re

from backend.library.pdf_text import PDFTextIndex
from backend.retrieval.searxng import SearXNGSearch

from .evidence import build_evidence, build_source
from .models import Evidence, ResearchRequest, Source


_LOCAL_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "how", "in", "is", "it", "of", "on", "or", "the",
    "this", "to", "was", "what", "when", "where", "which",
    "who", "why", "with", "trial", "study",
}


class ResearchPipeline:
    """Retrieve evidence from local PDFs and web search."""

    def __init__(
        self,
        searcher: SearXNGSearch | None = None,
        pdf_index: PDFTextIndex | None = None,
    ) -> None:
        self.searcher = searcher or SearXNGSearch()
        self.pdf_index = pdf_index or PDFTextIndex()

    @staticmethod
    def _local_query(question: str) -> str:
        terms = re.findall(r"[a-zA-Z0-9]+", question.lower())
        terms = [
            term for term in terms
            if term not in _LOCAL_STOP_WORDS and len(term) > 1
        ]
        # Quote terms so punctuation and FTS operators in the
        # original question cannot break the SQLite FTS query.
        return " OR ".join(f'"{term}"' for term in dict.fromkeys(terms))

    def retrieve(
        self,
        request: ResearchRequest,
    ) -> tuple[list[Source], list[Evidence]]:
        sources: list[Source] = []
        evidence: list[Evidence] = []
        limit = max(1, request.max_sources)

        # Reserve space for web sources where possible.
        local_limit = max(1, limit // 2)
        query = self._local_query(request.question)

        if query:
            try:
                local_results = self.pdf_index.search(
                    query, limit=local_limit
                )
            except Exception:
                # A local index problem must not disable web research.
                local_results = []

            for result in local_results:
                excerpt = (result.get("excerpt") or "").strip()
                title = (result.get("title") or "").strip()
                parent_key = (result.get("parent_key") or "").strip()

                if not excerpt or not title or not parent_key:
                    continue

                source_id = f"SRC-{len(sources) + 1:03d}"
                evidence_id = f"EVD-{len(evidence) + 1:03d}"

                sources.append(Source(
                    source_id=source_id,
                    title=f"{title} (Zotero key: {parent_key}"
                          f"{'; PDF p. ' + str(result['page']) if result.get('page') is not None else ''})",
                    url=None,
                    authors=[
                        author.strip()
                        for author in (result.get("creators") or "").split(";")
                        if author.strip()
                    ],
                    year=result.get("year"),
                    source_type="local_pdf",
                ))
                evidence.append(Evidence(
                    evidence_id=evidence_id,
                    source_id=source_id,
                    content=excerpt,
                    location=result.get("filename"),
                    page=result.get("page"),
                ))

        remaining = limit - len(sources)
        if remaining > 0:
            try:
                results = self.searcher.search(
                    request.question,
                    limit=remaining,
                )
            except Exception:
                if not evidence:
                    raise
                results = []

            for result in results:
                if not result.content.strip():
                    continue

                index = len(sources) + 1
                source = build_source(result, index)
                item = build_evidence(result, source, index)
                sources.append(source)
                evidence.append(item)

        return sources, evidence
