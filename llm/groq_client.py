import os
import sys
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import GROQ_API_KEY, GROQ_MODEL
from llm.abstract_client import AbstractLLMClient

class GroqClient(AbstractLLMClient):
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        if not self.api_key:
            print("Warning: GROQ_API_KEY is not set.")
        self.client = Groq(api_key=self.api_key)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response from Groq: {str(e)}"
