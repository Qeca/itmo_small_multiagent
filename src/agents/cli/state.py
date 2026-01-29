from typing import TypedDict, Any, Optional


class CLIState(TypedDict):
    task: str
    commands: Optional[list[str]]
    results: Optional[list[dict]]
    messages: Optional[list]
    response: Optional[Any]
