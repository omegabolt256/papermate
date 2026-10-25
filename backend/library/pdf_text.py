from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx
from pypdf import PdfReader

from backend.library.index import DEFAULT_DB


class PDFTextIndex:
    """Index extracted PDF text locally without copying the source PDFs."""

    def __init__(self, db_path: str | Path = DEFAULT_DB) -> None:
        self.db_path = Path(db_path)

    @contextmanager
    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS pdf_documents (
                    attachment_key TEXT PRIMARY KEY,
                    parent_key TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page_count INTEGER NOT NULL DEFAULT 0,
                    extracted_text TEXT NOT NULL DEFAULT ''
                )
            """)
            db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pdf_text_fts USING fts5(
                    attachment_key UNINDEXED,
                    parent_key UNINDEXED,
                    filename,
                    extracted_text
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS pdf_pages (
                    attachment_key TEXT NOT NULL,
                    parent_key TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    page_text TEXT NOT NULL,
                    PRIMARY KEY (attachment_key, page_number)
                )
            """)
            db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pdf_pages_fts USING fts5(
                    attachment_key UNINDEXED,
                    parent_key UNINDEXED,
                    filename,
                    page_number UNINDEXED,
                    page_text
                )
            """)

    @staticmethod
    def _local_path(location: str) -> Path:
        parsed = urlparse(location)
        if parsed.scheme.lower() != "file":
            raise ValueError("Zotero did not return a local file URL.")

        path = unquote(parsed.path)
        if len(path) >= 3 and path[0] == "/" and path[2] == ":":
            path = path[1:]
        return Path(path)

    def sync(self, client) -> dict[str, int]:
        """Extract text from existing Zotero PDF attachments."""
        items = client.fetch_raw_items()
        attachments = [
            item for item in items
            if item.get("data", {}).get("itemType") == "attachment"
            and item.get("data", {}).get("contentType") == "application/pdf"
            and item.get("data", {}).get("parentItem")
        ]

        indexed = 0
        skipped = 0
        failures = 0

        with httpx.Client(
            timeout=20,
            trust_env=False,
            headers={"Zotero-API-Version": "3"},
        ) as http:
            for item in attachments:
                data = item["data"]
                key = item.get("key", "")
                parent = data["parentItem"]
                filename = data.get("filename") or data.get("title") or key

                try:
                    response = http.get(
                        f"{client.base_url}/api/users/0/items/{key}/file",
                        follow_redirects=False,
                    )
                    if response.status_code != 302:
                        failures += 1
                        continue

                    path = self._local_path(response.headers.get("Location", ""))
                    if not path.is_file():
                        failures += 1
                        continue

                    reader = PdfReader(str(path))
                    if reader.is_encrypted:
                        skipped += 1
                        continue

                    page_texts = [
                        (page.extract_text() or "").strip()
                        for page in reader.pages
                    ]
                    text = "\n\n".join(page_texts).strip()

                    if not text:
                        skipped += 1
                        continue

                    with self.connect() as db:
                        db.execute("""
                            INSERT INTO pdf_documents
                                (attachment_key, parent_key, filename,
                                 page_count, extracted_text)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(attachment_key) DO UPDATE SET
                                parent_key = excluded.parent_key,
                                filename = excluded.filename,
                                page_count = excluded.page_count,
                                extracted_text = excluded.extracted_text
                        """, (key, parent, filename, len(reader.pages), text))

                        db.execute(
                            "DELETE FROM pdf_text_fts WHERE attachment_key = ?",
                            (key,),
                        )
                        db.execute("""
                            INSERT INTO pdf_text_fts
                                (attachment_key, parent_key, filename, extracted_text)
                            VALUES (?, ?, ?, ?)
                        """, (key, parent, filename, text))

                        db.execute(
                            "DELETE FROM pdf_pages WHERE attachment_key = ?",
                            (key,),
                        )
                        db.execute(
                            "DELETE FROM pdf_pages_fts WHERE attachment_key = ?",
                            (key,),
                        )
                        for page_number, page_text in enumerate(page_texts, 1):
                            if not page_text:
                                continue
                            db.execute("""
                                INSERT INTO pdf_pages
                                    (attachment_key, parent_key, filename,
                                     page_number, page_text)
                                VALUES (?, ?, ?, ?, ?)
                            """, (key, parent, filename, page_number, page_text))
                            db.execute("""
                                INSERT INTO pdf_pages_fts
                                    (attachment_key, parent_key, filename,
                                     page_number, page_text)
                                VALUES (?, ?, ?, ?, ?)
                            """, (key, parent, filename, page_number, page_text))

                    indexed += 1
                except Exception:
                    failures += 1

        return {
            "attachments_found": len(attachments),
            "indexed": indexed,
            "skipped": skipped,
            "failures": failures,
        }

    def status(self) -> dict[str, int]:
        """Return counts for the local PDF text index."""
        self.initialize()
        with self.connect() as db:
            row = db.execute("""
                SELECT COUNT(*) AS document_count,
                       COALESCE(SUM(page_count), 0) AS page_count,
                       COALESCE(SUM(LENGTH(extracted_text)), 0) AS character_count
                FROM pdf_documents
            """).fetchone()

        return {
            "document_count": int(row["document_count"]),
            "page_count": int(row["page_count"]),
            "character_count": int(row["character_count"]),
        }

    def search(self, query: str, limit: int = 20) -> list[dict]:
        query = query.strip()
        if not query:
            return []

        terms = list(dict.fromkeys(re.findall(r"[A-Za-z0-9]+", query)))
        if not terms:
            return []

        self.initialize()
        with self.connect() as db:
            all_terms_query = " AND ".join(f'"{term}"' for term in terms)
            any_terms_query = " OR ".join(f'"{term}"' for term in terms)

            sql = """
                SELECT f.parent_key, p.title, p.creators, p.year,
                       f.filename, CAST(f.page_number AS INTEGER) AS page,
                       snippet(pdf_pages_fts, 4, '[', ']', '...', 50) AS excerpt,
                       f.page_text AS full_text,
                       rank AS fts_rank
                FROM pdf_pages_fts f
                LEFT JOIN papers p ON p.zotero_key = f.parent_key
                WHERE pdf_pages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            candidate_limit = max(limit * 5, 100)
            rows = db.execute(sql, (all_terms_query, candidate_limit)).fetchall()
            if not rows:
                rows = db.execute(sql, (any_terms_query, candidate_limit)).fetchall()

            # Re-rank retrieved pages using full page text; retain FTS rank as tie-breaker.
            if rows and len(terms) > 1:
                term_patterns = [
                    re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
                    for term in terms
                ]

                def relevance(row):
                    text = row["full_text"] or ""
                    coverage = sum(bool(pattern.search(text)) for pattern in term_patterns)
                    return (-coverage, float(row["fts_rank"]))

                rows = sorted(rows, key=relevance)

            # Backward-compatible fallback for indexes not yet re-synced.
            if not rows:
                legacy_sql = """
                    SELECT f.parent_key, p.title, p.creators, p.year,
                           f.filename, NULL AS page,
                           snippet(pdf_text_fts, 3, '[', ']', '...', 50) AS excerpt
                    FROM pdf_text_fts f
                    LEFT JOIN papers p ON p.zotero_key = f.parent_key
                    WHERE pdf_text_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """
                rows = db.execute(
                    legacy_sql, (all_terms_query, limit)
                ).fetchall()
                if not rows:
                    rows = db.execute(
                        legacy_sql, (any_terms_query, limit)
                    ).fetchall()

        return [dict(row) for row in rows[:limit]]
