from typing import TypedDict, Optional


class OrchestratorState(TypedDict):
    user_input: str
    analyst_decision: Optional[dict]
    agent_result: Optional[dict]
    final_answer: str
    iteration: int
