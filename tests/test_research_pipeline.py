from backend.research.models import ResearchRequest
from backend.research.pipeline import ResearchPipeline


def main() -> None:
    print("=== PaperMate Research Pipeline Test ===")

    request = ResearchRequest(
        question="randomized controlled trials",
        max_sources=3,
    )

    pipeline = ResearchPipeline()

    sources, evidence = pipeline.retrieve(request)

    print("Sources:", len(sources))
    print("Evidence:", len(evidence))

    assert sources
    assert evidence
    assert len(sources) == len(evidence)

    for source, item in zip(sources, evidence):
        print()
        print("SOURCE:", source.title)
        print("URL:", source.url)
        print("EVIDENCE:", item.content[:180])

        assert source.source_id == item.source_id
        assert item.content

    print()
    print("Retrieval → Evidence: PASS")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()