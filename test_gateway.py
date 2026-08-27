from intelligence.contracts import (
    IntelligenceRequest,
    TaskType,
)
from intelligence.gateway import IntelligenceGateway
from intelligence.providers.ollama import OllamaProvider


def main():
    request = IntelligenceRequest(
        messages=[
            {
                "role": "user",
                "content": (
                    "Reply with exactly: "
                    "PAPERMATE LOCAL OK"
                ),
            }
        ],
        task_type=TaskType.CHAT,
        max_tokens=50,
    )

    gateway = IntelligenceGateway(
        provider=OllamaProvider(
            model="qwen2.5:3b"
        )
    )

    result = gateway.generate(request)

    print("=== PaperMate v2 Ollama Test ===")
    print("Text:", result.text)
    print("Provider:", result.provider)
    print("Model:", result.model)
    print("Fallback:", result.fallback_used)
    print(
        "Latency:",
        result.timing.latency_ms,
        "ms",
    )
    print("Provenance:", result.provenance)


if __name__ == "__main__":
    main()