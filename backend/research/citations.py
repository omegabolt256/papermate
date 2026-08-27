from __future__ import annotations

import re

from .models import Claim, Evidence, Source


class CitationError(ValueError):
    pass


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "new",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "these",
    "this",
    "to",
    "used",
    "use",
    "what",
    "which",
    "with",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())

    normalized: set[str] = set()

    for word in words:
        if word in _STOP_WORDS:
            continue

        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("ing") and len(word) > 5:
            word = word[:-3]
        elif word.endswith("ed") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 4:
            word = word[:-1]

        normalized.add(word)

    return normalized


def _claim_proposition_tokens(claim: Claim) -> set[str]:
    generic_research_terms = {
        "randomiz",
        "controlled",
        "trial",
        "study",
        "experiment",
        "participant",
        "group",
        "treatment",
    }

    return _tokens(claim.text) - generic_research_terms


def _evidence_supports_claim(
    claim: Claim,
    item: Evidence,
) -> bool:
    proposition_tokens = _claim_proposition_tokens(claim)
    evidence_tokens = _tokens(item.content)

    if not proposition_tokens or not evidence_tokens:
        return False

    overlap = proposition_tokens & evidence_tokens

    coverage = len(overlap) / len(proposition_tokens)

    return coverage >= 0.40


def _combined_evidence_supports_claim(
    claim: Claim,
    cited_evidence: list[Evidence],
) -> bool:
    """
    Determine whether the combined cited evidence supports the claim.

    Evidence IDs attached to a claim are treated collectively. A single
    evidence item does not need to support every part of a multi-part
    claim when the combined evidence does.
    """

    proposition_tokens = _claim_proposition_tokens(claim)

    if not proposition_tokens:
        return False

    combined_tokens: set[str] = set()

    for item in cited_evidence:
        combined_tokens.update(
            _tokens(item.content)
        )

    overlap = proposition_tokens & combined_tokens

    coverage = len(overlap) / len(proposition_tokens)

    return coverage >= 0.40


def validate_answer_claim_coverage(
    answer: str,
    claims: list[Claim],
) -> None:
    """
    Ensure every meaningful factual statement in the answer
    is represented by at least one claim.

    Coverage is checked sentence-by-sentence.
    """

    if not answer.strip():
        raise CitationError(
            "Answer contains no usable content."
        )

    if not claims:
        raise CitationError(
            "Answer contains content but no claims."
        )

    sentences = re.split(
        r"(?<=[.!?])\s+",
        answer.strip(),
    )

    meaningful_sentences = [
        sentence.strip()
        for sentence in sentences
        if _tokens(sentence.strip())
    ]

    if not meaningful_sentences:
        raise CitationError(
            "Answer contains no meaningful terms."
        )

    claim_token_sets = [
        _tokens(claim.text)
        for claim in claims
    ]

    for sentence in meaningful_sentences:
        sentence_tokens = _tokens(sentence)

        covered = False

        for claim_tokens in claim_token_sets:
            if not claim_tokens:
                continue

            overlap = sentence_tokens & claim_tokens

            coverage = (
                len(overlap)
                / len(sentence_tokens)
            )

            if coverage >= 0.60:
                covered = True
                break

        if not covered:
            raise CitationError(
                "Answer contains factual content that is not "
                "represented in the claims."
            )


def validate_claim_citations(
    claims: list[Claim],
    evidence: list[Evidence],
    sources: list[Source],
) -> None:
    evidence_map = {
        item.evidence_id: item
        for item in evidence
    }

    source_ids = {
        source.source_id
        for source in sources
    }

    for claim in claims:
        if not claim.evidence_ids:
            raise CitationError(
                f"Claim {claim.claim_id} has no supporting evidence."
            )

        cited_evidence: list[Evidence] = []

        for evidence_id in claim.evidence_ids:
            item = evidence_map.get(evidence_id)

            if item is None:
                raise CitationError(
                    f"Claim {claim.claim_id} references "
                    f"unknown evidence: {evidence_id}"
                )

            if not item.content.strip():
                raise CitationError(
                    f"Evidence {evidence_id} contains no usable content."
                )

            if item.source_id not in source_ids:
                raise CitationError(
                    f"Evidence {evidence_id} references "
                    f"unknown source: {item.source_id}"
                )

            cited_evidence.append(item)

        if not _combined_evidence_supports_claim(
            claim,
            cited_evidence,
        ):
            raise CitationError(
                f"Cited evidence does not sufficiently "
                f"support claim {claim.claim_id}."
            )