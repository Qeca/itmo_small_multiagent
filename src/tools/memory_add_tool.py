from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.memory import MemoryAgent


class MemoryAddInput(BaseModel):
    text: str = Field(description="Текст для сохранения в память (действия агента, результаты)")
    agent: str = Field(description="Имя агента, который выполнил действие")
    action: str = Field(description="Тип действия (code_execution, cli_command, search, etc)")


class AddToMemoryTool(BaseTool):
    name: str = "add_to_memory"
    description: str = (
        "Сохраняет действия и результаты агентов в векторную память. "
        "Используй это для записи того, что делали другие агенты. "
        "ТОЛЬКО для Orchestrator."
    )
    args_schema: type[BaseModel] = MemoryAddInput
    memory: MemoryAgent = None
    
    def __init__(self, memory: MemoryAgent):
        super().__init__(memory=memory)
    
    def _run(self, text: str, agent: str, action: str) -> str:
        metadata = {
            "agent": agent,
            "action": action
        }
        
        result = self.memory.add(text, metadata)
        return f"💾 {result}"
    
    async def _arun(self, text: str, agent: str, action: str) -> str:
        return self._run(text, agent, action)
