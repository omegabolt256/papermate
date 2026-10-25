import json
import unittest
from unittest.mock import Mock

from backend.research.models import Evidence, Source
from backend.research.synthesis import synthesize


class SynthesisValidationTests(unittest.TestCase):
    def setUp(self):
        self.sources = [
            Source(source_id="SRC-001", title="Test study",
                   url="https://example.org/study")
        ]
        self.evidence = [
            Evidence(evidence_id="EVD-001", source_id="SRC-001",
                     content="The trial included 200 participants.")
        ]

    def provider(self, claims, answer="The trial included 200 participants."):
        mock = Mock()
        mock.generate.return_value = json.dumps({
            "answer": answer,
            "claims": claims,
        })
        return mock

    def test_accepts_valid_claim_and_builds_answer_from_claims(self):
        provider = self.provider([{
            "claim_id": "CLM-001",
            "text": "The trial included 200 participants.",
            "evidence_ids": ["EVD-001"],
        }], answer="Untrusted extra answer text.")

        result = synthesize(
            provider, "How many participants?", self.sources, self.evidence
        )

        self.assertEqual(
            result.answer, "The trial included 200 participants."
        )
        self.assertEqual(result.claims[0].evidence_ids, ["EVD-001"])

    def test_rejects_duplicate_claim_ids(self):
        provider = self.provider([
            {"claim_id": "CLM-001", "text": "First claim.",
             "evidence_ids": ["EVD-001"]},
            {"claim_id": "CLM-001", "text": "Second claim.",
             "evidence_ids": ["EVD-001"]},
        ])

        with self.assertRaisesRegex(ValueError, "Duplicate claim_id"):
            synthesize(provider, "Question?", self.sources, self.evidence)

    def test_rejects_empty_claim_id(self):
        provider = self.provider([{
            "claim_id": " ",
            "text": "A claim.",
            "evidence_ids": ["EVD-001"],
        }])

        with self.assertRaisesRegex(ValueError, "claim_id"):
            synthesize(provider, "Question?", self.sources, self.evidence)

    def test_rejects_unknown_evidence_id(self):
        provider = self.provider([{
            "claim_id": "CLM-001",
            "text": "A claim.",
            "evidence_ids": ["EVD-999"],
        }])

        with self.assertRaisesRegex(ValueError, "EVD-999"):
            synthesize(provider, "Question?", self.sources, self.evidence)


if __name__ == "__main__":
    unittest.main()
