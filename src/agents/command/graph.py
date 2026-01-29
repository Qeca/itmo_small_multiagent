from langgraph.graph import StateGraph, END

from src.agents.command.state import CommandState
from src.agents.command.node import CommandNode
from src.utils import AgentLogger


def build_command_graph(tools: list, logger: AgentLogger = None):
    node = CommandNode(tools, logger)
    
    workflow = StateGraph(CommandState)
    
    workflow.add_node("start", node.start)
    workflow.add_node("call_tools", node.call_tools)
    workflow.add_node("debug", node.debug)
    workflow.add_node("review", node.review)
    
    workflow.set_entry_point("start")
    
    workflow.add_conditional_edges(
        "start",
        node.should_continue,
        {
            "call_tools": "call_tools",
            "review": "review"
        }
    )
    
    workflow.add_conditional_edges(
        "call_tools",
        node.should_debug_or_review,
        {
            "call_tools": "call_tools",
            "debug": "debug",
            "review": "review"
        }
    )
    
    workflow.add_conditional_edges(
        "debug",
        node.should_debug_or_review,
        {
            "call_tools": "call_tools",
            "debug": "debug",
            "review": "review"
        }
    )
    
    workflow.add_edge("review", END)
    
    return workflow.compile()
