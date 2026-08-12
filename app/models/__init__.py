"""Model provider abstraction."""
from abc import ABC, abstractmethod
from typing import Optional
import requests
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class OllamaProvider(ModelProvider):
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or OLLAMA_MODEL
        self.base_url = base_url or OLLAMA_BASE_URL
    
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.3),
                        "num_predict": kwargs.get("max_tokens", 600)
                    }
                },
                timeout=160
            )
            if response.status_code == 200:
                return response.json()["response"]
            return f"Error: HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "Error: Ollama request timed out. Is the model loaded?"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Is it running?"
        except Exception as e:
            return f"Error: {e}"

def get_model_provider(provider_type: str = "ollama", **kwargs) -> ModelProvider:
    if provider_type == "ollama":
        return OllamaProvider(**kwargs)
    raise ValueError(f"Unknown provider: {provider_type}")