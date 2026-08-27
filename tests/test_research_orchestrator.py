from backend.research.models import ResearchRequest
from backend.research.orchestrator import ResearchOrchestrator


def main() -> None:
    print("=== PaperMate End-to-End Research Test ===")

    request = ResearchRequest(
        question="What are randomized controlled trials used for?",
        max_sources=3,
        require_citations=True,
    )

    orchestrator = ResearchOrchestrator()

    response = orchestrator.research(request)

    print()
    print("ANSWER:")
    print(response.answer)

    print()
    print("SOURCES:", len(response.sources))
    print("EVIDENCE:", len(response.evidence))
    print("CLAIMS:", len(response.claims))
    print("CITATIONS:", len(response.citations))
    print("REFERENCES:", len(response.references))

    print()
    print("PROVENANCE:")
    print(response.provenance)

    assert response.answer
    assert response.sources
    assert response.evidence
    assert response.claims
    assert response.citations
    assert response.references

    assert response.provenance["citation_validation"] == "passed"

    for citation in response.citations:
        assert citation["citation_id"]
        assert citation["source_id"]
        assert citation["title"]
        assert citation["evidence_ids"]

    print()
    print("End-to-end research: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()