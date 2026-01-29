from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.core.executor import CodeExecutor


class CodeExecutorInput(BaseModel):
    code: str = Field(description="Python код для выполнения")


class CodeExecutorTool(BaseTool):
    name: str = "execute_python_code"
    description: str = (
        "Выполняет Python код в изолированной среде. "
        "Используй для вычислений, обработки данных, ML, работы с библиотеками."
    )
    args_schema: type[BaseModel] = CodeExecutorInput
    executor: CodeExecutor = None
    
    def __init__(self):
        super().__init__(executor=CodeExecutor())
    
    def _run(self, code: str) -> str:
        result = self.executor.run(code)
        
        if result["status"] == "success":
            return f"✅ Успешно выполнено:\n{result['output']}"
        else:
            return f"❌ Ошибка:\n{result['traceback']}"
    
    async def _arun(self, code: str) -> str:
        return self._run(code)
