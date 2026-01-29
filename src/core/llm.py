from openai import OpenAI

from src.config import Settings


class LLMClient:
    def __init__(self, settings: Settings):
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url
        )
        self.model = settings.model
    
    def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    
    def chat_messages(self, messages: list[dict], temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
