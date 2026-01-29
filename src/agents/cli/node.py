from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from src.prompts import PromptLoader
from src.agents.cli.state import CLIState
from src.utils import AgentLogger
from src.config import Settings


class CLINode:
    def __init__(self, tools: list, logger: AgentLogger = None):
        settings = Settings()
        self.llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            temperature=0.7
        ).bind_tools(tools)
        
        self.prompts = PromptLoader()
        self.logger = logger
        self.tools = {tool.name: tool for tool in tools}
    
    def start(self, state: CLIState) -> dict:
        if self.logger:
            self.logger.agent_start("CLI Agent", state["task"])
            self.logger.thinking("CLI Agent")
        
        prompt = self.prompts.load("cli_agent")
        
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=state["task"])
        ]
        
        response = self.llm.invoke(messages)
        
        if self.logger:
            if response.content:
                self.logger.stream_start("CLI Agent response")
                self.logger.stream_token(response.content)
                self.logger.stream_end()
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                self.logger.step(f"Tool calls: {[t['name'] for t in response.tool_calls]}")
        
        return {
            "messages": messages,
            "response": response,
            "commands": [],
            "results": []
        }
    
    def call_tools(self, state: CLIState) -> dict:
        response = state["response"]
        messages = state.get("messages", [])
        commands = state.get("commands", [])
        results = state.get("results", [])
        
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            return {}
        
        messages.append(AIMessage(content=response.content or "", tool_calls=response.tool_calls))
        
        for tool_call in response.tool_calls:
            tool = self.tools.get(tool_call["name"])
            if tool:
                if tool_call["name"] == "execute_shell_command":
                    command = tool_call["args"]["command"]
                    commands.append(command)
                    
                    if self.logger:
                        self.logger.cli_commands([command])
                
                if self.logger:
                    self.logger.tool_start(tool_call["name"], tool_call["args"])
                
                tool_result = tool.invoke(tool_call["args"])
                
                if self.logger:
                    success = "❌" not in tool_result if isinstance(tool_result, str) else True
                    self.logger.tool_end(tool_call["name"], success, tool_result if tool_call["name"] in ["search_memory", "search_web"] else None)
                
                if tool_call["name"] == "execute_shell_command":
                    if "✅" in tool_result:
                        clean_output = tool_result.replace("✅ ", "").strip()
                        status = "success"
                    else:
                        clean_output = tool_result.replace("❌ Ошибка: ", "").replace("❌ ", "").strip()
                        status = "error"
                    
                    results.append({
                        "command": command,
                        "result": {"status": status, "output": clean_output}
                    })
                    
                    if self.logger:
                        self.logger.cli_result(results[-1])
                
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
        
        response = self.llm.invoke(messages)
        
        return {
            "messages": messages,
            "response": response,
            "commands": commands,
            "results": results
        }
    
    def should_continue(self, state: CLIState) -> str:
        response = state.get("response")
        
        if not response:
            return "end"
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return "call_tools"
        
        return "end"
