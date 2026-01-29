from typing import TypedDict, Any, Optional


class CommandState(TypedDict):
    task: str
    code: Optional[str]
    result: Optional[dict]
    review: Optional[str]
    messages: Optional[list]
    response: Optional[Any]
    retry_count: int
