from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class LLMRequest(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt: str


class ToolCall(BaseModel):
    id: Optional[str] = None
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    content: str
    tool_calls: List[ToolCall] = []
    tool_outputs: List[Dict[str, Any]] = []
