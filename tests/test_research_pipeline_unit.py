import unittest
from unittest.mock import Mock

from backend.research.models import ResearchRequest
from backend.research.pipeline import ResearchPipeline


class ResearchPipelineTests(unittest.TestCase):
    def setUp(self):
        self.web = Mock()
        self.pdf = Mock()
        self.pipeline = ResearchPipeline(
            searcher=self.web,
            pdf_index=self.pdf,
        )
        self.web.search.return_value = []
        self.pdf.search.return_value = []

    def test_combines_local_and_web_sources_with_unique_ids(self):
        self.pdf.search.return_value = [{
            "parent_key": "PAPER1",
            "title": "Local Study",
            "creators": "A Author",
            "year": 2020,
            "filename": "study.pdf",
            "excerpt": "Dapagliflozin improved kidney outcomes.",
        }]
        self.web.search.return_value = [
            Mock(
                title="Web Study",
                url="https://example.org/study",
                content="The trial evaluated kidney outcomes.",
            )
        ]

        sources, evidence = self.pipeline.retrieve(
            ResearchRequest(
                question="What is the DAPA-CKD trial?",
                max_sources=4,
            )
        )

        self.assertEqual(len(sources), 2)
        self.assertEqual(len(evidence), 2)
        self.assertEqual(
            [source.source_type for source in sources],
            ["local_pdf", "web"],
        )
        self.assertEqual(
            len({source.source_id for source in sources}), 2
        )
        self.assertEqual(
            len({item.evidence_id for item in evidence}), 2
        )
        self.assertEqual(
            [item.source_id for item in evidence],
            [source.source_id for source in sources],
        )

    def test_local_index_failure_still_uses_web(self):
        self.pdf.search.side_effect = RuntimeError("index unavailable")
        self.web.search.return_value = [
            Mock(
                title="Web Study",
                url="https://example.org/study",
                content="Relevant study evidence.",
            )
        ]

        sources, evidence = self.pipeline.retrieve(
            ResearchRequest(question="kidney study", max_sources=3)
        )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_type, "web")
        self.assertEqual(len(evidence), 1)

    def test_empty_local_and_web_results_return_empty_lists(self):
        sources, evidence = self.pipeline.retrieve(
            ResearchRequest(question="kidney study", max_sources=3)
        )

        self.assertEqual(sources, [])
        self.assertEqual(evidence, [])


if __name__ == "__main__":
    unittest.main()
