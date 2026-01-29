import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from src.prompts import PromptLoader
from src.agents.analyst.state import AnalystState
from src.utils import AgentLogger
from src.config import Settings


def extract_json(text: str) -> dict:
    text = text.strip()
    
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1).strip()
    
    brace_match = re.search(r'\{[\s\S]*\}', text)
    if brace_match:
        text = brace_match.group(0)
    
    return json.loads(text)


class AnalystNode:
    def __init__(self, tools: list, logger: AgentLogger = None):
        settings = Settings()
        
        search_tools = [t for t in tools if t.name in ["search_web", "search_memory"]]
        
        self.llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            temperature=0.7
        ).bind_tools(search_tools)
        
        self.prompts = PromptLoader()
        self.logger = logger
        self.tools = {tool.name: tool for tool in search_tools}
    
    def analyze(self, state: AnalystState) -> dict:
        if self.logger:
            self.logger.agent_start("Analyst", state["user_input"])
            self.logger.thinking("Analyst")
        
        prompt = self.prompts.load("analyst")
        
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=state["user_input"])
        ]
        
        response = self.llm.invoke(messages)
        
        if self.logger:
            if response.content:
                self.logger.stream_start("Analyst decision")
                self.logger.stream_token(response.content)
                self.logger.stream_end()
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                self.logger.step(f"Tool calls: {[t['name'] for t in response.tool_calls]}")
        
        return {
            "decision": {
                "agent": "processing",
                "reasoning": "Analyzing",
                "task": response.content if response.content else "",
                "response": response,
                "messages": messages
            }
        }
    
    def call_tools(self, state: AnalystState) -> dict:
        decision = state["decision"]
        response = decision.get("response")
        messages = decision.get("messages", [])
        
        if not hasattr(response, 'tool_calls') or not response.tool_calls:
            return {}
        
        messages.append(AIMessage(content=response.content or "", tool_calls=response.tool_calls))
        
        for tool_call in response.tool_calls:
            tool = self.tools.get(tool_call["name"])
            if tool:
                if self.logger:
                    self.logger.tool_start(tool_call["name"], tool_call["args"])
                
                result = tool.invoke(tool_call["args"])
                
                if self.logger:
                    success = "❌" not in str(result) if result else True
                    self.logger.tool_end(tool_call["name"], success, str(result))
                
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        
        response = self.llm.invoke(messages)
        
        return {
            "decision": {
                "agent": "processing",
                "reasoning": "Analyzing with tools results",
                "task": response.content if response.content else "",
                "response": response,
                "messages": messages
            }
        }
    
    def finalize(self, state: AnalystState) -> dict:
        decision = state["decision"]
        response = decision.get("response")
        
        content = response.content if hasattr(response, 'content') else str(response)
        
        try:
            final_decision = extract_json(content)
        except (json.JSONDecodeError, AttributeError):
            final_decision = {
                "agent": "FINISH",
                "reasoning": "Could not parse decision",
                "task": content
            }
        
        if self.logger:
            self.logger.agent_decision(final_decision)
        
        return {"decision": final_decision}
    
    def should_continue(self, state: AnalystState) -> str:
        decision = state.get("decision", {})
        response = decision.get("response")
        
        if not response:
            return "finalize"
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return "call_tools"
        
        return "finalize"
