import logging
import os
from typing import Any

import requests

from src.tools import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GetRepresentativeTelephoneTool(BaseTool):
    def __init__(self) -> None:
        self.api_endpoint = os.getenv("DIFY_TELEPHONE_API_ENDPOINT", "")
        self.api_key = os.getenv("DIFY_TELEPHONE_API_KEY", "")
        self.name = "get_representative_telephone"
        self.description = "This function retrieves the representative's phone number from a company name. Only execute when specifically requested to obtain a phone number."
        self.parameters: dict[str, Any] = {
            "type": "object",
            "properties": {
                "company": {
                    "type": "string",
                    "description": "Company name (e.g. Google, Toyota, CyberAgent)",
                }
            },
            "required": ["company"],
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
        company = kwargs.get("company")
        if not company:
            raise ValueError("company is required")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data: dict[str, Any] = {
            "inputs": {"input": company},
            "response_mode": "blocking",
            "user": "abc",
        }

        logger.info(f"GetRepresentativeTelephoneTool: request post")
        try:
            response = requests.post(
                f"{self.api_endpoint}/workflows/run",
                headers=headers,
                json=data,
                timeout=(10.0, 30.0),
            )
        except Exception as e:
            logger.error(f"GetRepresentativeTelephoneTool: error {e}")
            return "Failed to get telephone number"
        logger.info(f"GetRepresentativeTelephoneTool: get {response=}")

        response.raise_for_status()
        body = response.json()
        telephone = body["data"]["outputs"]["output"]

        return telephone


if __name__ == "__main__":
    tool = GetRepresentativeTelephoneTool()
    query = "Google"
    try:
        telephone = tool.run(company=query)
        print(telephone)
    except Exception as e:
        print(f"An error occurred: {e}")
