from typing import Dict


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, object] = {}

    def register(self, name: str, tool: object) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> object:
        return self._tools[name]
