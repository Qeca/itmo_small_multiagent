from langgraph.graph import StateGraph, END

from src.agents.orchestrator.state import OrchestratorState
from src.agents.orchestrator.node import OrchestratorNode
from src.memory import MemoryAgent
from src.utils import AgentLogger


def build_orchestrator_graph(analyst_graph, command_graph, cli_graph, tools: list, memory: MemoryAgent, logger: AgentLogger = None):
    node = OrchestratorNode(analyst_graph, command_graph, cli_graph, tools, memory, logger)
    
    workflow = StateGraph(OrchestratorState)
    
    workflow.add_node("analyst", node.route_to_analyst)
    workflow.add_node("execute_agent", node.route_to_agent)
    workflow.add_node("finalize", node.format_final_answer)
    
    workflow.set_entry_point("analyst")
    
    workflow.add_conditional_edges(
        "analyst",
        node.should_continue,
        {
            "continue": "execute_agent",
            "finish": "finalize"
        }
    )
    
    workflow.add_edge("execute_agent", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()
