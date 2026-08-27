from backend.intelligence.context_compressor import ContextCompressor
from backend.tools.registry import ToolRegistry


def main() -> None:
    print("=== PaperMate Tools + Compression Test ===")

    compressor = ContextCompressor()

    text = (
        "A" * 8000
        + " DOI: 10.1234/example.paper "
        + " https://example.org/paper"
        + " B" * 8000
    )

    compressed = compressor.compress_context(text)

    print(f"Original chars:   {len(text)}")
    print(f"Compressed chars: {len(compressed)}")

    assert len(compressed) <= 14000
    assert "10.1234/example.paper" in compressed
    assert "https://example.org/paper" in compressed

    registry = ToolRegistry()

    registry.register(
        "test_tool",
        "Simple registry validation tool",
        lambda value: f"TOOL OK: {value}",
    )

    result = registry.call(
        "test_tool",
        value="PaperMate",
    )

    print(f"Tool result: {result}")

    assert result == "TOOL OK: PaperMate"
    assert len(registry.list()) == 1

    print("STATUS: PASS")


if __name__ == "__main__":
    main()