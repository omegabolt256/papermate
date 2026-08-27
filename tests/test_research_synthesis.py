from backend.intelligence.providers.ollama import OllamaProvider
from backend.research.models import ResearchRequest
from backend.research.pipeline import ResearchPipeline
from backend.research.synthesis import synthesize
from backend.research.citations import validate_claim_citations


def main() -> None:
    print("=== PaperMate Research Synthesis Test ===")

    request = ResearchRequest(
        question="What are randomized controlled trials used for?",
        max_sources=3,
    )

    pipeline = ResearchPipeline()

    sources, evidence = pipeline.retrieve(request)

    print("Sources:", len(sources))
    print("Evidence:", len(evidence))

    provider = OllamaProvider(
        model="qwen2.5:3b",
    )

    result = synthesize(
        provider,
        request.question,
        sources,
        evidence,
    )

    print()
    print("ANSWER:")
    print(result.answer)

    print()
    print("CLAIMS:", len(result.claims))

    for claim in result.claims:
        print()
        print("CLAIM:", claim.claim_id)
        print("TEXT:", claim.text)
        print("EVIDENCE:", claim.evidence_ids)

    validate_claim_citations(
        claims=result.claims,
        evidence=evidence,
        sources=sources,
    )

    print()
    print("Citation validation: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()