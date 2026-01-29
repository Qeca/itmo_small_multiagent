from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from src.prompts import PromptLoader
from src.agents.command.state import CommandState
from src.config import Settings
from src.utils import AgentLogger


def clean_code_block(code: str) -> str:
    code = code.strip()
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    elif code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    return code


class CommandNode:
    def __init__(self, tools: list, logger: AgentLogger = None):
        settings = Settings()
        self.llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            temperature=0.7
        ).bind_tools(tools)
        
        self.prompts = PromptLoader()
        self.settings = settings
        self.logger = logger
        self.tools = {tool.name: tool for tool in tools}
    
    def start(self, state: CommandState) -> dict:
        if self.logger:
            self.logger.agent_start("Command Agent", state["task"])
            self.logger.thinking("Command Agent")
        
        prompt = self.prompts.load("command_agent")
        
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=state["task"])
        ]
        
        response = self.llm.invoke(messages)
        
        if self.logger:
            if response.content:
                self.logger.stream_start("Command Agent response")
                self.logger.stream_token(response.content)
                self.logger.stream_end()
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                self.logger.step(f"Tool calls: {[t['name'] for t in response.tool_calls]}")
        
        return {
            "messages": messages,
            "response": response,
            "code": None,
            "result": None,
            "retry_count": state.get("retry_count", 0)
        }
    
    def call_tools(self, state: CommandState) -> dict:
        response = state["response"]
        messages = state.get("messages", [])
        
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            return {}
        
        messages.append(AIMessage(content=response.content or "", tool_calls=response.tool_calls))
        
        code = None
        result = None
        
        for tool_call in response.tool_calls:
            tool = self.tools.get(tool_call["name"])
            if tool:
                if tool_call["name"] == "execute_python_code":
                    code = tool_call["args"]["code"]
                    if self.logger:
                        self.logger.code_generated(code)
                
                if self.logger:
                    self.logger.tool_start(tool_call["name"], tool_call["args"])
                
                tool_result = tool.invoke(tool_call["args"])
                
                if self.logger:
                    success = "❌" not in tool_result if isinstance(tool_result, str) else True
                    self.logger.tool_end(tool_call["name"], success, tool_result if tool_call["name"] in ["search_memory", "search_web"] else None)
                
                if tool_call["name"] == "execute_python_code":
                    if "✅" in tool_result:
                        clean_output = tool_result.replace("✅ Успешно выполнено:\n", "").strip()
                        result = {"status": "success", "output": clean_output}
                    else:
                        clean_output = tool_result.replace("❌ Ошибка:\n", "").strip()
                        result = {"status": "error", "output": clean_output}
                    
                    if self.logger:
                        self.logger.code_result(result)
                
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
        
        response = self.llm.invoke(messages)
        
        return {
            "messages": messages,
            "response": response,
            "code": code or state.get("code"),
            "result": result or state.get("result")
        }
    
    def debug(self, state: CommandState) -> dict:
        retry_count = state.get("retry_count", 0) + 1
        
        if self.logger:
            self.logger.debug_attempt(retry_count, 3)
        
        code = state.get("code", "")
        result = state.get("result", {})
        error = result.get("output", str(result)) if isinstance(result, dict) else str(result)
        
        prompt = self.prompts.format(
            "code_debugger",
            code=code,
            error=error
        )
        
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=prompt["user"])
        ]
        
        response = self.llm.invoke(messages)
        fixed_code = clean_code_block(response.content)
        
        if self.logger:
            self.logger.code_generated(fixed_code)
        
        tool = self.tools.get("execute_python_code")
        if tool:
            if self.logger:
                self.logger.tool_start("execute_python_code", {"code": fixed_code})
            
            tool_result = tool.invoke({"code": fixed_code})
            
            if "✅" in tool_result:
                clean_output = tool_result.replace("✅ Успешно выполнено:\n", "").strip()
                new_result = {"status": "success", "output": clean_output}
            else:
                clean_output = tool_result.replace("❌ Ошибка:\n", "").strip()
                new_result = {"status": "error", "output": clean_output}
            
            if self.logger:
                success = new_result["status"] == "success"
                self.logger.tool_end("execute_python_code", success)
                self.logger.code_result(new_result)
            
            return {
                "code": fixed_code,
                "result": new_result,
                "retry_count": retry_count
            }
        
        return {"retry_count": retry_count}
    
    def review(self, state: CommandState) -> dict:
        if self.logger:
            self.logger.step("Reviewing results...")
        
        result = state.get("result", {})
        result_output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
        
        prompt = self.prompts.format(
            "code_reviewer",
            code=state.get("code", ""),
            result=result_output
        )
        
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=prompt["user"])
        ]
        
        response = self.llm.invoke(messages)
        review = response.content
        
        if self.logger:
            self.logger.code_review(review)
        
        return {"review": review}
    
    def should_continue(self, state: CommandState) -> str:
        response = state.get("response")
        
        if not response:
            return "review"
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return "call_tools"
        
        return "review"
    
    def should_debug_or_review(self, state: CommandState) -> str:
        result = state.get("result")
        response = state.get("response")
        retry_count = state.get("retry_count", 0)
        
        if result is None:
            if response and hasattr(response, 'tool_calls') and response.tool_calls:
                return "call_tools"
            return "review"
        
        if isinstance(result, dict) and result.get("status") == "error":
            if retry_count < 3:
                return "debug"
        
        return "review"
