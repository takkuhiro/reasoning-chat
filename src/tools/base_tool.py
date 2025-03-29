from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = ""
        self.parameters: dict[str, Any] = {}
        self.definition: dict[str, Any] = {}

    @abstractmethod
    def run(self) -> str:
        pass
