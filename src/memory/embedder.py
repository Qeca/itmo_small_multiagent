import numpy as np
from openai import OpenAI

from src.config import Settings


class APIEmbedder:
    def __init__(self):
        settings = Settings()
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url
        )
        self.model = settings.embedding_model
    
    def encode(self, texts: list[str]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )
        
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype=np.float32)
