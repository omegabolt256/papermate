import sys
from pathlib import Path

# Add PaperMate project root to Python's import path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.research.models import ResearchRequest
from backend.research.orchestrator import ResearchOrchestrator


def main():
    print("=== PaperMate Research Core Test ===")

    request = ResearchRequest(
        question="What does the evidence say about randomized trials?",
        project_id="papermate-test",
    )

    response = ResearchOrchestrator().research(request)

    print("Answer:", response.answer)
    print("Sources:", len(response.sources))
    print("Evidence:", len(response.evidence))
    print("Claims:", len(response.claims))
    print(
        "Citation validation:",
        response.provenance["citation_validation"],
    )

    assert response.sources
    assert response.evidence
    assert response.claims
    assert response.provenance["citation_validation"] == "passed"

    print("STATUS: PASS")


if __name__ == "__main__":
    main()