import faiss
import numpy as np
from datetime import datetime

from src.memory.embedder import APIEmbedder
from src.config import Settings


class MemoryAgent:
    def __init__(self):
        settings = Settings()
        self.embedder = APIEmbedder()
        self.index = faiss.IndexFlatL2(settings.embedding_dim)
        self.store = {}
        self.counter = 0
    
    def add(self, text: str, metadata: dict = None) -> str:
        timestamp = datetime.now().isoformat()
        
        chunk = {
            "id": self.counter,
            "text": text,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        
        emb = self.embedder.encode([text])
        self.index.add(emb)
        self.store[self.counter] = chunk
        
        self.counter += 1
        
        return f"Saved to memory with ID: {chunk['id']}"
    
    def search(self, query: str, k: int = 3) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        
        q_emb = self.embedder.encode([query])
        distances, indices = self.index.search(q_emb, min(k, self.index.ntotal))
        
        results = []
        for idx in indices[0]:
            if idx in self.store:
                results.append(self.store[idx])
        
        return results
    
    def get_all(self) -> list[dict]:
        return list(self.store.values())
    
    def get_recent(self, n: int = 5) -> list[dict]:
        all_items = self.get_all()
        return sorted(all_items, key=lambda x: x["timestamp"], reverse=True)[:n]
