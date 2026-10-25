from __future__ import annotations

import json
from dataclasses import dataclass

from backend.intelligence.providers.base import IntelligenceProvider

from .models import Claim, Evidence, Source


@dataclass
class SynthesisResult:
    answer: str
    claims: list[Claim]


def build_evidence_context(
    sources: list[Source],
    evidence: list[Evidence],
) -> str:
    source_map = {
        source.source_id: source
        for source in sources
    }

    blocks: list[str] = []

    for item in evidence:
        source = source_map.get(item.source_id)

        if source is None:
            continue

        blocks.append(
            "\n".join(
                [
                    f"[{item.evidence_id}]",
                    f"Source: {source.title}",
                    f"URL: {source.url or 'N/A'}",
                    f"Evidence: {item.content}",
                ]
            )
        )

    return "\n\n".join(blocks)


def build_synthesis_prompt(
    question: str,
    sources: list[Source],
    evidence: list[Evidence],
) -> str:
    context = build_evidence_context(
        sources,
        evidence,
    )

    # Keep the JSON example outside the f-string so that
    # JSON braces cannot be interpreted as format fields.
    output_format = """
{
  "answer": "evidence-grounded answer",
  "claims": [
    {
      "claim_id": "CLM-001",
      "text": "supported factual claim",
      "evidence_ids": ["EVD-001", "EVD-003"]
    }
  ]
}
""".strip()

    return f"""
You are PaperMate's evidence-grounded research synthesizer.

QUESTION:
{question}

EVIDENCE:
{context}

RULES:
1. Use only information directly supported by the supplied evidence.
2. Do not invent facts, sources, URLs, statistics, quotations, or citations.
3. If the evidence is insufficient, explicitly say so.
4. Every factual statement in the answer must correspond to a claim.
5. Every claim must reference ALL evidence IDs that support that claim.
6. Do not combine multiple factual statements into the answer unless the claims section contains corresponding support for each statement.
7. Distinguish evidence from interpretation.
8. Do not treat search-result ranking as evidence quality.
9. Do not cite a source unless the supplied evidence supports the claim.
10. Prefer narrower claims over broader claims when evidence is limited.
11. If only one part of a proposed statement is supported, state only that supported part.
12. Each claim must contain exactly ONE independently verifiable factual statement.
13. Never combine trial design, outcomes, population, and implications into a single claim.
14. Assign evidence IDs separately to each claim; cite only excerpts that directly support that claim.
15. Keep each claim concise. Split compound sentences into multiple claims with unique sequential IDs.
16. The answer must contain only claims represented in the claims array.


Return JSON only.

OUTPUT FORMAT:
{output_format}
""".strip()


def synthesize(
    provider: IntelligenceProvider,
    question: str,
    sources: list[Source],
    evidence: list[Evidence],
) -> SynthesisResult:

    prompt = build_synthesis_prompt(
        question,
        sources,
        evidence,
    )

    raw = provider.generate(
        prompt,
        temperature=0.0,
        max_tokens=1200,
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Ollama returned invalid JSON."
        ) from exc

    raw_claims = data.get("claims")

    if not isinstance(raw_claims, list):
        raise ValueError(
            "Synthesis response contains no valid claims list."
        )

    evidence_ids = {
        item.evidence_id
        for item in evidence
    }

    claims: list[Claim] = []
    seen_claim_ids: set[str] = set()

    for item in raw_claims:
        if not isinstance(item, dict):
            raise ValueError(
                "Invalid claim object returned by model."
            )

        claim_id = item.get("claim_id")
        text = item.get("text")
        raw_evidence_ids = item.get("evidence_ids")

        if not isinstance(claim_id, str) or not claim_id.strip():
            raise ValueError("Claim has invalid or empty claim_id.")

        if claim_id in seen_claim_ids:
            raise ValueError(f"Duplicate claim_id: {claim_id}")

        seen_claim_ids.add(claim_id)

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"Claim {claim_id} has invalid text."
            )

        if not isinstance(raw_evidence_ids, list):
            raise ValueError(
                f"Claim {claim_id} has invalid evidence_ids."
            )

        if not raw_evidence_ids:
            raise ValueError(
                f"Claim {claim_id} has no evidence IDs."
            )

        claim_evidence_ids = [
            str(value)
            for value in raw_evidence_ids
        ]

        unknown_ids = [
            evidence_id
            for evidence_id in claim_evidence_ids
            if evidence_id not in evidence_ids
        ]

        if unknown_ids:
            raise ValueError(
                f"Claim {claim_id} references unknown "
                f"evidence IDs: {unknown_ids}"
            )

        claims.append(
            Claim(
                claim_id=claim_id,
                text=text.strip(),
                evidence_ids=claim_evidence_ids,
            )
        )

    if not claims:
        raise ValueError(
            "Synthesis produced no claims."
        )

    # Claims are the canonical evidence-grounded answer.
    # Do not trust the model's free-form answer because it may
    # contain unsupported additional statements.
    canonical_answer = " ".join(
        claim.text
        for claim in claims
        if claim.text.strip()
    )

    if not canonical_answer:
        raise ValueError(
            "Synthesis produced no usable answer."
        )

    return SynthesisResult(
        answer=canonical_answer,
        claims=claims,
    )