from backend.tools.memory import MemPalaceTool


def main():
    print("=== PaperMate MemPalace Tool Test ===")

    memory = MemPalaceTool()

    print("\n[1] STORE")

    memory.store(
        "PaperMate uses MemPalace for long-term research memory.",
        wing="papermate",
        room="architecture",
        source_file="memory-test",
    )

    print("Stored: PASS")

    print("\n[2] SEARCH")

    results = memory.search(
        "PaperMate MemPalace long-term research memory",
        wing="papermate",
        room="architecture",
        limit=5,
    )

    print(f"Results: {len(results)}")

    if not results:
        raise RuntimeError("MemPalace returned no search results.")

    for result in results:
        print("\nCONTENT:")
        print(result.content)
        print("SCORE:", result.score)

    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()