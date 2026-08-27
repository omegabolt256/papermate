from backend.research.searxng_search import SearXNGResearchSearcher


def main():
    print("=== PaperMate SearXNG Search Test ===")

    searcher = SearXNGResearchSearcher()

    results = searcher.search(
        "randomized controlled trials",
        max_results=3,
    )

    print("Results:", len(results))

    for result in results:
        print()
        print("ID:", result.source_id)
        print("Title:", result.title)
        print("URL:", result.url)
        print("Snippet:", result.snippet[:150])

    assert results

    for result in results:
        assert result.source_id
        assert result.title
        assert result.url

    print("\nSearXNG search: PASS")
    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()