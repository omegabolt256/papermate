from backend.research.models import ResearchRequest
from backend.research.orchestrator import ResearchOrchestrator
from backend.research.serialization import serialize_research_response


def main() -> None:
    print("=== PaperMate Research Serialization Test ===")

    request = ResearchRequest(
        question="What are randomized controlled trials used for?",
        max_sources=3,
        require_citations=True,
    )

    response = ResearchOrchestrator().research(request)

    data = serialize_research_response(response)

    print("Keys:", list(data.keys()))

    assert data["answer"]
    assert data["sources"]
    assert data["evidence"]
    assert data["claims"]
    assert data["citations"]
    assert data["references"]
    assert data["provenance"]

    print("Answer:", data["answer"])
    print("Sources:", len(data["sources"]))
    print("Citations:", len(data["citations"]))

    print()
    print("Serialization: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()