import logging
import os
from typing import Any

import requests

from src.tools import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSearchTool(BaseTool):
    def __init__(self) -> None:
        self.api_endpoint = os.getenv("DIFY_GOOGLESEARCH_API_ENDPOINT", "")
        self.api_key = os.getenv("DIFY_GOOGLESEARCH_API_KEY", "")
        self.name = "googlesearch"
        self.description = "A function to perform Google search. Returns Google search results for the input keywords."
        self.parameters: dict[str, Any] = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Enter keywords separated by spaces.",
                }
            },
            "required": ["query"],
        }
        self.definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, **kwargs) -> str:
        query = kwargs.get("query")
        if not query:
            raise ValueError("query is required")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": {
                "query": query,
            },
            "response_mode": "blocking",
            "user": "abc",
        }
        try:
            response = requests.post(
                f"{self.api_endpoint}/workflows/run",
                headers=headers,
                json=payload,
                timeout=(10.0, 30.0),
            )
        except Exception as e:
            logger.error(f"GoogleSearchTool: request post error: {e}")
            return "Failed to retrieve results"

        response.raise_for_status()
        result = response.json()["data"]["outputs"]["result"]
        logger.info(f"GoogleSearchTool: get {result=}")
        return result


if __name__ == "__main__":
    tool = GoogleSearchTool()
    try:
        body = tool.run(query="AI Agent")
        print(body)
    except Exception as e:
        print(f"An error occurred: {e}")
