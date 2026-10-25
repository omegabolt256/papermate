import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend.library.pdf_text import PDFTextIndex


class FakeZoteroClient:
    base_url = "http://127.0.0.1:23119"

    def fetch_raw_items(self):
        return [{
            "key": "PDF123",
            "data": {
                "itemType": "attachment",
                "contentType": "application/pdf",
                "parentItem": "PAPER123",
                "filename": "study.pdf",
            },
        }]


class PDFTextIndexTests(unittest.TestCase):
    def make_http_mock(self, location):
        response = Mock(status_code=302)
        response.headers = {"Location": location}
        http = Mock()
        http.__enter__ = Mock(return_value=http)
        http.__exit__ = Mock(return_value=False)
        http.get.return_value = response
        return http

    def test_initialize_and_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = PDFTextIndex(Path(tmp) / "test.sqlite3")
            index.initialize()

            with index.connect() as db:
                db.execute("""
                    CREATE TABLE papers (
                        zotero_key TEXT PRIMARY KEY,
                        title TEXT,
                        creators TEXT,
                        year INTEGER
                    )
                """)
                db.execute(
                    "INSERT INTO papers VALUES (?, ?, ?, ?)",
                    ("PAPER123", "Dapagliflozin Study", "Test Author", 2020),
                )
                text = "Dapagliflozin improved kidney outcomes."
                db.execute("""
                    INSERT INTO pdf_documents
                    (attachment_key, parent_key, filename, page_count, extracted_text)
                    VALUES (?, ?, ?, ?, ?)
                """, ("PDF123", "PAPER123", "study.pdf", 3, text))
                db.execute("""
                    INSERT INTO pdf_text_fts
                    (attachment_key, parent_key, filename, extracted_text)
                    VALUES (?, ?, ?, ?)
                """, ("PDF123", "PAPER123", "study.pdf", text))

            results = index.search("dapagliflozin")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["parent_key"], "PAPER123")
            self.assertEqual(results[0]["filename"], "study.pdf")
            self.assertEqual(results[0]["title"], "Dapagliflozin Study")

    def test_empty_query_returns_no_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = PDFTextIndex(Path(tmp) / "test.sqlite3")
            self.assertEqual(index.search("   "), [])

    def test_status_reports_empty_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = PDFTextIndex(Path(tmp) / "test.sqlite3")
            status = index.status()
            self.assertEqual(status["document_count"], 0)
            self.assertEqual(status["page_count"], 0)
            self.assertEqual(status["character_count"], 0)

    def test_sync_twice_updates_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = PDFTextIndex(root / "test.sqlite3")
            index.initialize()
            pdf_path = root / "study.pdf"
            pdf_path.write_bytes(b"mock PDF")
            client = FakeZoteroClient()
            http = self.make_http_mock(pdf_path.as_uri())

            readers = [
                Mock(
                    is_encrypted=False,
                    pages=[Mock(extract_text=Mock(return_value=text))],
                )
                for text in (
                    "First dapagliflozin text",
                    "Updated kidney outcomes text",
                )
            ]

            with patch("backend.library.pdf_text.httpx.Client", return_value=http), \
                 patch("backend.library.pdf_text.PdfReader", side_effect=readers):
                first = index.sync(client)
                second = index.sync(client)

            self.assertEqual(first["indexed"], 1)
            self.assertEqual(second["indexed"], 1)

            db = sqlite3.connect(root / "test.sqlite3")
            try:
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM pdf_documents").fetchone()[0], 1
                )
                self.assertEqual(
                    db.execute("SELECT COUNT(*) FROM pdf_text_fts").fetchone()[0], 1
                )
                stored = db.execute(
                    "SELECT extracted_text FROM pdf_documents WHERE attachment_key=?",
                    ("PDF123",),
                ).fetchone()[0]
            finally:
                db.close()

            self.assertEqual(stored, "Updated kidney outcomes text")

    def test_unreadable_pdf_is_counted_as_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = PDFTextIndex(Path(tmp) / "test.sqlite3")
            index.initialize()
            http = self.make_http_mock((Path(tmp) / "missing.pdf").as_uri())

            with patch("backend.library.pdf_text.httpx.Client", return_value=http):
                result = index.sync(FakeZoteroClient())

            self.assertEqual(result["failures"], 1)
            self.assertEqual(result["indexed"], 0)


if __name__ == "__main__":
    unittest.main()
