from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.memory import MemoryAgent


class MemorySearchInput(BaseModel):
    query: str = Field(description="Поисковый запрос для поиска в истории памяти")


class SearchMemoryTool(BaseTool):
    name: str = "search_memory"
    description: str = (
        "Ищет в истории выполненных задач и действий агентов. "
        "Используй чтобы найти похожие решения, код, команды из прошлых задач. "
        "Доступен всем агентам."
    )
    args_schema: type[BaseModel] = MemorySearchInput
    memory: MemoryAgent = None
    
    def __init__(self, memory: MemoryAgent):
        super().__init__(memory=memory)
    
    def _run(self, query: str) -> str:
        results = self.memory.search(query, k=3)
        
        if not results:
            return "🔍 Ничего не найдено в памяти. Это первая подобная задача."
        
        output = ["🧠 Найдено в истории памяти:\n"]
        
        for idx, item in enumerate(results, 1):
            output.append(f"{idx}. [{item['metadata'].get('agent', 'unknown')}] {item['metadata'].get('action', 'action')}")
            output.append(f"   Время: {item['timestamp']}")
            output.append(f"   {item['text'][:200]}...")
            output.append("")
        
        return "\n".join(output)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
