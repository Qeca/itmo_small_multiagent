from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.config import Settings


class TavilySearchInput(BaseModel):
    query: str = Field(description="Поисковый запрос для поиска в интернете")


class TavilySearchTool(BaseTool):
    name: str = "search_web"
    description: str = (
        "Ищет актуальную информацию в интернете через Tavily. "
        "Используй для поиска документации, примеров кода, решений проблем, "
        "актуальных версий библиотек, API референсов."
    )
    args_schema: type[BaseModel] = TavilySearchInput
    tavily: TavilySearchResults = None
    
    def __init__(self):
        settings = Settings()
        super().__init__(
            tavily=TavilySearchResults(
                api_key=settings.tavily_api_key,
                max_results=3
            )
        )
    
    def _run(self, query: str) -> str:
        results = self.tavily.invoke({"query": query})
        
        if not results:
            return "Информация не найдена."
        
        output = ["🔍 Найдено в интернете:\n"]
        
        for idx, result in enumerate(results, 1):
            output.append(f"{idx}. {result.get('content', '')}")
            output.append(f"   Источник: {result.get('url', '')}\n")
        
        return "\n".join(output)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
