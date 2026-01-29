from langchain_openai import ChatOpenAI

from src.agents.orchestrator.state import OrchestratorState
from src.utils import AgentLogger
from src.memory import MemoryAgent
from src.config import Settings


class OrchestratorNode:
    def __init__(self, analyst_graph, command_graph, cli_graph, tools: list, memory: MemoryAgent, logger: AgentLogger = None):
        self.analyst = analyst_graph
        self.command_agent = command_graph
        self.cli_agent = cli_graph
        self.memory = memory
        self.logger = logger
        
        settings = Settings()
        self.llm = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            temperature=0.7
        ).bind_tools(tools)
        
        self.tools = {tool.name: tool for tool in tools}
    
    def route_to_analyst(self, state: OrchestratorState) -> dict:
        if self.logger and state.get("iteration", 0) == 0:
            self.logger.agent_start("Orchestrator", state["user_input"])
        
        if self.logger:
            self.logger.progress("Routing to Analyst...")
        
        result = self.analyst.invoke({
            "user_input": state["user_input"]
        })
        
        return {
            "analyst_decision": result["decision"],
            "iteration": state.get("iteration", 0) + 1
        }
    
    def route_to_agent(self, state: OrchestratorState) -> dict:
        decision = state["analyst_decision"]
        agent_name = decision["agent"]
        task = decision["task"]
        
        if agent_name == "command_agent":
            if self.logger:
                self.logger.progress("Routing to Command Agent...")
            
            result = self.command_agent.invoke({"task": task, "retry_count": 0})
            agent_result = {
                "agent": "command_agent",
                "code": result["code"],
                "result": result["result"],
                "review": result.get("review", "")
            }
            
            if self.logger:
                self.logger.progress("Saving to memory...")
            
            memory_text = f"Task: {task}\nCode: {result['code']}\nResult: {result['result']}"
            self.memory.add(memory_text, {"agent": "command_agent", "action": "code_execution"})
            
        elif agent_name == "cli_agent":
            if self.logger:
                self.logger.progress("Routing to CLI Agent...")
            
            result = self.cli_agent.invoke({"task": task})
            agent_result = {
                "agent": "cli_agent",
                "commands": result["commands"],
                "results": result["results"]
            }
            
            if self.logger:
                self.logger.progress("Saving to memory...")
            
            memory_text = f"Task: {task}\nCommands: {result['commands']}\nResults: {result['results']}"
            self.memory.add(memory_text, {"agent": "cli_agent", "action": "cli_execution"})
            
        else:
            agent_result = {
                "agent": "none",
                "message": task
            }
        
        return {"agent_result": agent_result}
    
    def format_final_answer(self, state: OrchestratorState) -> dict:
        decision = state["analyst_decision"]
        
        if decision["agent"] == "FINISH":
            answer = f"📝 Ответ:\n{decision['task']}"
        else:
            agent_result = state["agent_result"]
            
            if agent_result["agent"] == "command_agent":
                result = agent_result.get("result")
                code = agent_result.get("code", "")
                review = agent_result.get("review", "")
                
                has_result = result is not None and result != {} and (
                    not isinstance(result, dict) or result.get("status") in ["success", "error"]
                )
                
                if not has_result:
                    answer = "⚠️ Код не был выполнен\n"
                    answer += "=" * 40 + "\n\n"
                    answer += "Агент не вызвал execute_python_code.\n"
                    if review:
                        answer += f"\n📋 Ревью:\n{review}"
                else:
                    if isinstance(result, dict):
                        output = result.get("output", "")
                        status = result.get("status", "error")
                    else:
                        output = str(result)
                        status = "error"
                    
                    answer = "📊 Результат выполнения Python кода\n"
                    answer += "=" * 40 + "\n\n"
                    
                    if status == "success":
                        answer += f"✅ Статус: Успешно\n\n"
                    else:
                        answer += f"❌ Статус: Ошибка\n\n"
                    
                    answer += f"📤 Вывод:\n{output if output else '(нет вывода)'}\n"
                    
                    if code:
                        code_preview = code[:200] + "..." if len(code) > 200 else code
                        answer += f"\n💻 Код (preview):\n{code_preview}\n"
                    
                    if review:
                        answer += f"\n📋 Ревью:\n{review}"
                    
            elif agent_result["agent"] == "cli_agent":
                answer = "💻 Результаты выполнения CLI команд\n"
                answer += "=" * 40 + "\n\n"
                
                for i, item in enumerate(agent_result.get("results", []), 1):
                    cmd = item.get('command', '')
                    result = item.get("result", {})
                    
                    if isinstance(result, dict):
                        output = result.get("output", "")
                        status = result.get("status", "unknown")
                    else:
                        output = str(result)
                        status = "success"
                    
                    emoji = "✅" if status == "success" else "❌"
                    answer += f"{emoji} $ {cmd}\n"
                    if output:
                        answer += f"   {output}\n"
                    answer += "\n"
            else:
                answer = f"📝 {agent_result.get('message', 'Нет результата')}"
        
        if self.logger:
            self.logger.final_answer(answer)
        
        return {"final_answer": answer}
    
    def should_continue(self, state: OrchestratorState) -> str:
        if state.get("iteration", 0) >= 5:
            return "finish"
        
        decision = state.get("analyst_decision", {})
        if decision.get("agent") == "FINISH":
            return "finish"
        
        return "continue"
