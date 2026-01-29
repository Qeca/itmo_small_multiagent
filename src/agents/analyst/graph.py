from langgraph.graph import StateGraph, END

from src.agents.analyst.state import AnalystState
from src.agents.analyst.node import AnalystNode
from src.utils import AgentLogger


def build_analyst_graph(tools: list, logger: AgentLogger = None):
    node = AnalystNode(tools, logger)
    
    workflow = StateGraph(AnalystState)
    
    workflow.add_node("analyze", node.analyze)
    workflow.add_node("call_tools", node.call_tools)
    workflow.add_node("finalize", node.finalize)
    
    workflow.set_entry_point("analyze")
    
    workflow.add_conditional_edges(
        "analyze",
        node.should_continue,
        {
            "call_tools": "call_tools",
            "finalize": "finalize"
        }
    )
    
    workflow.add_conditional_edges(
        "call_tools",
        node.should_continue,
        {
            "call_tools": "call_tools",
            "finalize": "finalize"
        }
    )
    
    workflow.add_edge("finalize", END)
    
    return workflow.compile()
