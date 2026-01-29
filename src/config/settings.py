import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "qwen/qwen3-embedding-8b")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "4096"))
    max_retries: int = 2
