from backend.api.research import create_research_api

def main() -> None:
    print("=== PaperMate Research API Test ===")

    api = create_research_api()

    result = api.research(
        "What are randomized controlled trials used for?",
        max_sources=3,
        require_citations=True,
    )

    print("Answer:", result["answer"])
    print("Sources:", len(result["sources"]))
    print("Evidence:", len(result["evidence"]))
    print("Claims:", len(result["claims"]))
    print("Citations:", len(result["citations"]))
    print("References:", len(result["references"]))

    assert result["answer"]
    assert result["sources"]
    assert result["evidence"]
    assert result["claims"]
    assert result["citations"]
    assert result["references"]

    assert result["provenance"]["citation_validation"] == "passed"

    print()
    print("API contract: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()