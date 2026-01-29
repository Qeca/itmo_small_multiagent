from langgraph.graph import StateGraph, END

from src.agents.cli.state import CLIState
from src.agents.cli.node import CLINode
from src.utils import AgentLogger


def build_cli_graph(tools: list, logger: AgentLogger = None):
    node = CLINode(tools, logger)
    
    workflow = StateGraph(CLIState)
    
    workflow.add_node("start", node.start)
    workflow.add_node("call_tools", node.call_tools)
    
    workflow.set_entry_point("start")
    
    workflow.add_conditional_edges(
        "start",
        node.should_continue,
        {
            "call_tools": "call_tools",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "call_tools",
        node.should_continue,
        {
            "call_tools": "call_tools",
            "end": END
        }
    )
    
    return workflow.compile()
