from src.memory import MemoryAgent
from src.utils import AgentLogger
from src.tools import (
    CodeExecutorTool,
    CLIExecutorTool,
    TavilySearchTool,
    AddToMemoryTool,
    SearchMemoryTool
)
from src.agents.analyst.graph import build_analyst_graph
from src.agents.command.graph import build_command_graph
from src.agents.cli.graph import build_cli_graph
from src.agents.orchestrator.graph import build_orchestrator_graph


class JARVIS:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = AgentLogger() if verbose else None
        
        self.memory = MemoryAgent()
        
        code_tool = CodeExecutorTool()
        cli_tool = CLIExecutorTool()
        tavily_tool = TavilySearchTool()
        search_memory_tool = SearchMemoryTool(self.memory)
        add_memory_tool = AddToMemoryTool(self.memory)
        
        analyst_tools = [search_memory_tool, tavily_tool]
        command_tools = [code_tool, search_memory_tool, tavily_tool]
        cli_tools = [cli_tool, search_memory_tool, tavily_tool]
        orchestrator_tools = [add_memory_tool, search_memory_tool, tavily_tool]
        
        self.analyst_graph = build_analyst_graph(analyst_tools, self.logger)
        self.command_graph = build_command_graph(command_tools, self.logger)
        self.cli_graph = build_cli_graph(cli_tools, self.logger)
        
        self.orchestrator = build_orchestrator_graph(
            self.analyst_graph,
            self.command_graph,
            self.cli_graph,
            orchestrator_tools,
            self.memory,
            self.logger
        )
    
    def run(self, task: str) -> str:
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"🚀 JARVIS запущен")
            print(f"📋 Задача: {task}")
            print(f"{'='*80}\n")
        
        result = self.orchestrator.invoke({
            "user_input": task,
            "analyst_decision": None,
            "agent_result": None,
            "final_answer": "",
            "iteration": 0
        })
        
        final_answer = result.get("final_answer", "Нет результата")
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"✅ Задача завершена")
            print(f"{'='*80}\n")
        
        return final_answer
