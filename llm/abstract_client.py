from abc import ABC, abstractmethod

class AbstractLLMClient(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Takes a system prompt and user prompt and returns the LLM response.
        """
        pass
