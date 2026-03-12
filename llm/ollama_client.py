import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL
from llm.abstract_client import AbstractLLMClient

class OllamaClient(AbstractLLMClient):
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "stream": False,
            "options": {
                "num_gpu": 99,       # Offload as many layers as possible
                "main_gpu": 0,      # Use the primary GPU
                "low_vram": False   # Don't use low vram mode if possible
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"Error generating response from Ollama: {str(e)}"
