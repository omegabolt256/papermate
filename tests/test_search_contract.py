from backend.research.mock_search import MockResearchSearcher


def main():
    print("=== PaperMate Search Contract Test ===")

    searcher = MockResearchSearcher()

    results = searcher.search(
        "randomized controlled trials",
        max_results=5,
    )

    print("Results:", len(results))

    assert results
    assert results[0].title
    assert results[0].source_id
    assert results[0].url

    print("Source discovery: PASS")
    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()