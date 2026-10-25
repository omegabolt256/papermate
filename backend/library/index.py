from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


DEFAULT_DB = Path("data/library/papermate_library.sqlite3")


class LibraryIndex:
    """Local metadata index; never modifies the Zotero library."""

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
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    zotero_key TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    creators TEXT NOT NULL DEFAULT '',
                    year INTEGER,
                    doi TEXT,
                    item_type TEXT NOT NULL DEFAULT '',
                    zotero_url TEXT,
                    date_added TEXT,
                    date_modified TEXT
                )
            """)

            connection.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts
                USING fts5(
                    zotero_key UNINDEXED,
                    title,
                    creators,
                    doi,
                    content='papers',
                    content_rowid='rowid'
                )
            """)

            connection.executescript("""
                CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
                    INSERT INTO papers_fts(rowid, zotero_key, title, creators, doi)
                    VALUES (new.rowid, new.zotero_key, new.title, new.creators, new.doi);
                END;

                CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
                    INSERT INTO papers_fts(
                        papers_fts, rowid, zotero_key, title, creators, doi
                    )
                    VALUES (
                        'delete', old.rowid, old.zotero_key,
                        old.title, old.creators, old.doi
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS papers_au AFTER UPDATE ON papers BEGIN
                    INSERT INTO papers_fts(
                        papers_fts, rowid, zotero_key, title, creators, doi
                    )
                    VALUES (
                        'delete', old.rowid, old.zotero_key,
                        old.title, old.creators, old.doi
                    );

                    INSERT INTO papers_fts(rowid, zotero_key, title, creators, doi)
                    VALUES (new.rowid, new.zotero_key, new.title, new.creators, new.doi);
                END;
            """)

    def status(self) -> dict[str, int | bool | str]:
        if not self.db_path.exists():
            return {
                "initialized": False,
                "paper_count": 0,
                "database": str(self.db_path),
            }

        self.initialize()
        with self.connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM papers"
            ).fetchone()[0]

        return {
            "initialized": True,
            "paper_count": count,
            "database": str(self.db_path),
        }

    def upsert_papers(self, papers: list[dict]) -> int:
        self.initialize()
        with self.connect() as connection:
            for paper in papers:
                connection.execute("""
                    INSERT INTO papers (
                        zotero_key, title, creators, year, doi, item_type,
                        zotero_url, date_added, date_modified
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(zotero_key) DO UPDATE SET
                        title = excluded.title,
                        creators = excluded.creators,
                        year = excluded.year,
                        doi = excluded.doi,
                        item_type = excluded.item_type,
                        zotero_url = excluded.zotero_url,
                        date_added = excluded.date_added,
                        date_modified = excluded.date_modified
                """, (
                    paper["zotero_key"],
                    paper.get("title", ""),
                    paper.get("creators", ""),
                    paper.get("year"),
                    paper.get("doi"),
                    paper.get("item_type", ""),
                    paper.get("zotero_url"),
                    paper.get("date_added"),
                    paper.get("date_modified"),
                ))
        return len(papers)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        query = query.strip()
        if not query:
            return []

        self.initialize()
        with self.connect() as connection:
            rows = connection.execute("""
                SELECT p.zotero_key, p.title, p.creators, p.year, p.doi,
                       p.item_type, p.zotero_url
                FROM papers_fts f
                JOIN papers p ON p.rowid = f.rowid
                WHERE papers_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit)).fetchall()

        return [dict(row) for row in rows]
