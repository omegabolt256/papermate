from backend.tools.memory import MemPalaceTool
from backend.tools.memory_tools import register_memory_tools
from backend.tools.registry import ToolRegistry


def main():
    print("=== PaperMate Tool Registry Test ===")

    registry = ToolRegistry()
    memory = MemPalaceTool()

    register_memory_tools(
        registry,
        memory,
    )

    tools = registry.list()

    print("\nRegistered tools:")

    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    expected = {
        "memory_search",
        "memory_store",
        "knowledge_graph",
    }

    actual = {tool.name for tool in tools}

    assert expected.issubset(actual)

    print("\nRegistry registration: PASS")

    results = registry.call(
        "memory_search",
        query="PaperMate long-term research memory",
        wing="papermate",
        limit=5,
    )

    print(f"Memory search results: {len(results)}")

    assert results

    print("Memory invocation: PASS")
    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()