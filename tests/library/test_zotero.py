import unittest

from backend.library.zotero import normalize_item


class ZoteroNormalizationTests(unittest.TestCase):
    def test_normalizes_article_metadata(self):
        item = {
            "key": "ABC123",
            "data": {
                "itemType": "journalArticle",
                "title": "Clinical Trials",
                "date": "2024-06",
                "DOI": "10.1234/example",
                "creators": [
                    {"firstName": "Ada", "lastName": "Lovelace"}
                ],
                "url": "https://example.org/article",
            },
        }

        paper = normalize_item(item)

        self.assertEqual(paper["zotero_key"], "ABC123")
        self.assertEqual(paper["year"], 2024)
        self.assertEqual(paper["creators"], "Ada Lovelace")
        self.assertEqual(paper["doi"], "10.1234/example")


    def test_attachment_contains_parent_relationship(self):
        item = {
            "key": "PDF123",
            "data": {
                "itemType": "attachment",
                "title": "article.pdf",
                "parentItem": "PAPER123",
                "filename": "article.pdf",
                "linkMode": "imported_file",
            },
        }

        data = item["data"]
        self.assertEqual(data["parentItem"], "PAPER123")
        self.assertEqual(data["filename"], "article.pdf")
        self.assertEqual(data["linkMode"], "imported_file")

    def test_skips_attachments(self):
        item = {
            "key": "PDF123",
            "data": {"itemType": "attachment", "title": "article.pdf"},
        }
        self.assertIsNone(normalize_item(item))


if __name__ == "__main__":
    unittest.main()
