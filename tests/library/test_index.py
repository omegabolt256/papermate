import tempfile
import unittest
from pathlib import Path

from backend.library.index import LibraryIndex


class LibraryIndexTests(unittest.TestCase):
    def test_status_before_initialization(self):
        with tempfile.TemporaryDirectory() as temp:
            index = LibraryIndex(Path(temp) / "library.sqlite3")
            self.assertFalse(index.status()["initialized"])

    def test_insert_update_and_search(self):
        with tempfile.TemporaryDirectory() as temp:
            index = LibraryIndex(Path(temp) / "library.sqlite3")
            index.upsert_papers([{
                "zotero_key": "ABC123",
                "title": "Randomized clinical trials",
                "creators": "Smith",
                "year": 2025,
                "doi": "10.1234/example",
            }])

            results = index.search("randomized")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["zotero_key"], "ABC123")

            index.upsert_papers([{
                "zotero_key": "ABC123",
                "title": "Updated clinical research",
                "creators": "Smith",
                "year": 2026,
            }])

            self.assertEqual(index.status()["paper_count"], 1)
            self.assertEqual(index.search("randomized"), [])
            self.assertEqual(len(index.search("updated")), 1)


if __name__ == "__main__":
    unittest.main()
