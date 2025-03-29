import os
from datetime import datetime
from pathlib import Path


class ExperimentalMemory:
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir

    def load(self) -> str:
        memory = ""
        for file in os.listdir(self.memory_dir):
            with open(Path(f"{self.memory_dir}/{file}"), "r") as f:
                memory += f.read()
        if memory:
            memory = (
                f"Please refer to the following past experiences: {memory}"
            )
        return memory

    def save(self, memory: str):
        today = datetime.now().strftime("%Y%m%d")
        file_path = Path(f"{self.memory_dir}/{today}.txt")
        with open(file_path, "a") as f:
            f.write(memory)
