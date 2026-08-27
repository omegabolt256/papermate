from backend.intelligence.providers.ollama import OllamaProvider
from backend.research.citations import validate_claim_citations
from backend.research.models import ResearchRequest
from backend.research.pipeline import ResearchPipeline
from backend.research.synthesis import synthesize
from backend.research.citation_renderer import render_research


def main() -> None:
    print("=== PaperMate Citation Renderer Test ===")

    request = ResearchRequest(
        question="What are randomized controlled trials used for?",
        max_sources=3,
    )

    pipeline = ResearchPipeline()

    sources, evidence = pipeline.retrieve(request)

    provider = OllamaProvider(
        model="qwen2.5:3b",
    )

    result = synthesize(
        provider,
        request.question,
        sources,
        evidence,
    )

    validate_claim_citations(
        claims=result.claims,
        evidence=evidence,
        sources=sources,
    )

    rendered = render_research(
        answer=result.answer,
        claims=result.claims,
        evidence=evidence,
        sources=sources,
    )

    print()
    print("ANSWER:")
    print(rendered.answer)

    print()
    print("CITATIONS:", len(rendered.citations))

    for citation in rendered.citations:
        print()
        print(citation.citation_id)
        print("SOURCE:", citation.title)
        print("URL:", citation.url)
        print("EVIDENCE:", citation.evidence_ids)

    assert rendered.answer
    assert rendered.citations
    assert rendered.references
    assert rendered.claims
    assert rendered.evidence

    for citation in rendered.citations:
        assert citation.source_id
        assert citation.title
        assert citation.evidence_ids

    print()
    print("Citation rendering: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()