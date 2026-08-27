from __future__ import annotations

import json
from dataclasses import dataclass

from backend.intelligence.providers.base import IntelligenceProvider

from backend.research.models import Claim, Evidence, Source

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

    output_format = """
{
  "answer": "evidence-grounded answer",
  "claims": [
    {
      "claim_id": "CLM-001",
      "text": "supported factual claim",
      "evidence_ids": ["EVD-001"]
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

1. Use ONLY information directly supported by the supplied evidence.

2. Do NOT use outside knowledge.

3. Do NOT invent facts, sources, URLs, statistics, quotations,
   interpretations, conclusions, or implications.

4. Every factual sentence in the answer MUST correspond directly
   to at least one claim in the claims array.

5. Every claim MUST have one or more supporting evidence IDs.

6. The claim text MUST express exactly what its evidence supports.
   Do not make the claim broader than the evidence.

7. The answer should be a concise combination of the claims.
   Do not add explanatory phrases that introduce new factual content.

8. Do NOT add phrases such as:
   - "providing a compelling evidence base"
   - "this demonstrates that"
   - "this proves that"
   - "therefore"
   - "this suggests"
   unless that exact conclusion is directly supported by the evidence.

9. Do not combine unrelated evidence into a broader conclusion.

10. If multiple claims are present, each factual statement must have
    a corresponding claim.

11. Prefer narrow, literal claims over broad paraphrases.

12. The answer MUST contain only information represented in the
    claims array.

13. Before returning the JSON, internally verify:
    - Every answer sentence is represented by a claim.
    - Every claim has supporting evidence.
    - Every evidence ID exists in the supplied evidence.
    - No sentence contains an unsupported additional assertion.

14. Return JSON only. Do not use markdown fences.

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

    answer = data.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError(
            "Synthesis response contains no valid answer."
        )

    raw_claims = data.get("claims")

    if not isinstance(raw_claims, list):
        raise ValueError(
            "Synthesis response contains no valid claims list."
        )

    claims: list[Claim] = []

    for item in raw_claims:
        if not isinstance(item, dict):
            raise ValueError(
                "Invalid claim object returned by model."
            )

        claim_id = item.get("claim_id")
        text = item.get("text")
        evidence_ids = item.get("evidence_ids")

        if not isinstance(claim_id, str):
            raise ValueError(
                "Claim has invalid claim_id."
            )

        if not isinstance(text, str):
            raise ValueError(
                f"Claim {claim_id} has invalid text."
            )

        if not isinstance(evidence_ids, list):
            raise ValueError(
                f"Claim {claim_id} has invalid evidence_ids."
            )

        if not evidence_ids:
            raise ValueError(
                f"Claim {claim_id} has no evidence IDs."
            )

        claims.append(
            Claim(
                claim_id=claim_id,
                text=text,
                evidence_ids=[
                    str(value)
                    for value in evidence_ids
                ],
            )
        )

    return SynthesisResult(
        answer=answer,
        claims=claims,
    )