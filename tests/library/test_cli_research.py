import contextlib
import io
import sys
import unittest
from unittest.mock import Mock, patch

import papermate


class ResearchCliTests(unittest.TestCase):
    def test_success_prints_answer_and_references(self):
        api = Mock()
        api.research.return_value = {
            "answer": "Evidence supports the conclusion [1].",
            "references": [{
                "title": "Example study",
                "year": 2024,
                "url": "https://example.org/study",
            }],
            "model_runs": [{"provider": "ollama", "model": "test-model"}],
        }

        stdout = io.StringIO()
        with patch.object(sys, "argv", ["papermate", "research", "test question"]), \
             patch("papermate.create_research_api", return_value=api), \
             contextlib.redirect_stdout(stdout):
            result = papermate.main()

        self.assertEqual(result, 0)
        self.assertIn("Evidence supports the conclusion", stdout.getvalue())
        self.assertIn("Example study", stdout.getvalue())
        self.assertIn("https://example.org/study", stdout.getvalue())
        api.research.assert_called_once_with(
            "test question",
            project_id=None,
            max_sources=10,
            require_citations=True,
        )

    def test_research_options_are_forwarded(self):
        api = Mock()
        api.research.return_value = {"answer": "Answer", "references": []}

        with patch.object(sys, "argv", [
            "papermate", "research", "kidney", "outcomes",
            "--max-sources", "5", "--project-id", "project-1",
            "--no-citations",
        ]), patch("papermate.create_research_api", return_value=api), \
             contextlib.redirect_stdout(io.StringIO()):
            result = papermate.main()

        self.assertEqual(result, 0)
        api.research.assert_called_once_with(
            "kidney outcomes",
            project_id="project-1",
            max_sources=5,
            require_citations=False,
        )

    def test_api_failure_returns_nonzero(self):
        api = Mock()
        api.research.side_effect = RuntimeError("test failure")
        stderr = io.StringIO()

        with patch.object(sys, "argv", ["papermate", "research", "test question"]), \
             patch("papermate.create_research_api", return_value=api), \
             contextlib.redirect_stderr(stderr), \
             contextlib.redirect_stdout(io.StringIO()):
            result = papermate.main()

        self.assertEqual(result, 1)
        self.assertIn("Research failed: test failure", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
