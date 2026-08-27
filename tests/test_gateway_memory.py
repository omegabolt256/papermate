from backend.intelligence.gateway import (
    IntelligenceGateway,
    IntelligenceRequest,
)
from backend.intelligence.providers.ollama import OllamaProvider
from backend.tools.memory import MemPalaceTool


def main():
    print("=== PaperMate Gateway + Memory Test ===")

    memory = MemPalaceTool()

    memory.store(
        "PaperMate is designed as a research assistant "
        "with long-term project memory.",
        wing="papermate-gateway-test",
        room="architecture",
        source_file="gateway-test",
    )

    gateway = IntelligenceGateway(
        provider=OllamaProvider(
            model="qwen2.5:3b"
        ),
        provider_name="ollama",
        model_name="qwen2.5:3b",
        memory=memory,
    )

    response = gateway.generate(
        IntelligenceRequest(
            task_type="chat",
            project_id="papermate-gateway-test",
            prompt=(
                "What is PaperMate designed to have?"
            ),
            max_tokens=100,
            temperature=0,
        )
    )

    print("\nResponse:")
    print(response.text)

    print("\nProvider:", response.provider)
    print("Model:", response.model)
    print("Memory used:", response.memory_used)
    print("Memory results:", response.memory_results)
    print("Provenance:", response.provenance)

    assert response.text.strip()
    assert response.memory_used
    assert response.memory_results > 0
    assert response.provenance["context_compressed"]

    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()