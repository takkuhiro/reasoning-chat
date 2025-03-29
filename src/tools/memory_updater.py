import logging
from pathlib import Path
from typing import Any

from src.memory import ExperimentalMemory
from src.tools import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryUpdaterTool(BaseTool):
    def __init__(self, memory: ExperimentalMemory) -> None:
        self.name = "memory_updater"
        self.description = (
            "Update the memory. If the user has a positive or negative comment on the answer to the question, save it as knowledge to the memory."
            "If there is no feedback from the user or the task is not completed, do not execute."
        )
        self.parameters: dict[str, Any] = {
            "type": "object",
            "properties": {
                "memory_sentences": {
                    "type": "string",
                    "description": "The sentences to save to the memory. Save the success experience or failure experience based on the user's feedback. The sentences must be one line. Include the tool used, its steps, and its arguments.",
                }
            },
            "required": ["memory_sentences"],
        }
        self.definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
        self.memory = memory

    def run(self, **kwargs) -> str:
        memory_sentences = kwargs.get("memory_sentences")
        if not memory_sentences:
            raise ValueError("memory_sentences is required")

        logger.info(f"MemoryUpdaterTool: save {memory_sentences=}")
        self.memory.save(memory_sentences)
        return f"Saved the experience to the memory."


if __name__ == "__main__":
    tool = MemoryUpdaterTool(ExperimentalMemory(Path("src/memories")))
    try:
        body = tool.run(memory_sentences="AI Agent")
        print(body)
    except Exception as e:
        print(f"An error occurred: {e}")
