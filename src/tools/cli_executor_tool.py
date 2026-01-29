from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.core.cli_executor import CLIExecutor


class CLIExecutorInput(BaseModel):
    command: str = Field(description="Shell команда для выполнения")


class CLIExecutorTool(BaseTool):
    name: str = "execute_shell_command"
    description: str = (
        "Выполняет команду в терминале. "
        "Используй для git, npm, файловых операций, системных команд."
    )
    args_schema: type[BaseModel] = CLIExecutorInput
    executor: CLIExecutor = None
    
    def __init__(self):
        super().__init__(executor=CLIExecutor())
    
    def _run(self, command: str) -> str:
        result = self.executor.run(command)
        
        if result["status"] == "success":
            stdout = result.get("stdout", "").strip()
            return f"✅ {stdout}" if stdout else "✅ Команда выполнена (нет вывода)"
        else:
            stderr = result.get("stderr", "").strip()
            return f"❌ Ошибка: {stderr}" if stderr else "❌ Команда завершилась с ошибкой"
    
    async def _arun(self, command: str) -> str:
        return self._run(command)
