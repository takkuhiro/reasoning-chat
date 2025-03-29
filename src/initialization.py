import os
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from src.core.openai_module import ChatOpenAIClient
from src.memory import ExperimentalMemory
from src.tools import (
    BaseTool,
    GetRepresentativeTelephoneTool,
    GoogleSearchTool,
    MemoryUpdaterTool,
)


def initialize() -> tuple[
    ChatOpenAIClient,
    ExperimentalMemory,
    list[BaseTool],
    list[dict],
    dict[str, dict[str, Any]],
]:
    client = ChatOpenAIClient(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    memory = ExperimentalMemory(Path("src/memories"))
    tools_instances: list[BaseTool] = [
        GetRepresentativeTelephoneTool(),
        GoogleSearchTool(),
        MemoryUpdaterTool(memory),
    ]
    tools = [instance.definition for instance in tools_instances]
    available_tools: dict[str, dict[str, Any]] = {
        instance.name: {
            "run": instance.run,
            "args": list(instance.parameters["properties"].keys()),
        }
        for instance in tools_instances
    }
    return client, memory, tools_instances, tools, available_tools
