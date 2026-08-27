from backend.intelligence.providers.ollama import OllamaProvider


def main():
    print("=== PaperMate Ollama Provider Test ===")

    provider = OllamaProvider(
        model="qwen2.5:3b"
    )

    response = provider.generate(
        "Reply with exactly: PAPER MATE OLLAMA OK",
        max_tokens=20,
        temperature=0,
    )

    print("Response:", response)

    assert response.strip()

    print("STATUS: PASS")


if __name__ == "__main__":
    main()