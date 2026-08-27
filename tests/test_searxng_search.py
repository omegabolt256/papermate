from backend.retrieval.searxng import SearXNGSearch


def main() -> None:
    print("=== PaperMate SearXNG Search Test ===")

    searcher = SearXNGSearch()

    results = searcher.search(
        "randomized controlled trials",
        limit=5,
    )

    print(f"Results: {len(results)}")

    if not results:
        raise RuntimeError("SearXNG returned no results.")

    for index, result in enumerate(results, start=1):
        print()
        print(f"[{index}] {result.title}")
        print(f"URL: {result.url}")
        print(f"Engine: {result.engine}")
        print(f"Score: {result.score}")

    print()
    print("SearXNG retrieval: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()