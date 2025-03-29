from typing import Any

from src.memory import ExperimentalMemory
from src.prompts import REASONING_PROMPT, SYSTEM_PROMPT


def get_main_messages(
    history: list[dict[str, Any]],
    available_tools_str: str,
    thought: str,
    experimental_memory: ExperimentalMemory,
) -> list[dict[str, Any]]:
    query = history[-1]["content"]

    # Reasoning's content is also included
    context = ""
    for h in history:
        if h["role"] == "user":
            context += f"User: {h['content']}\n"
        elif (
            h["role"] == "assistant"
            and h["content"]
            and not h["content"].startswith("Thought:")
        ):  # AI Agent's response (Thought is not included)
            context += f"AI Agent: {h['content']}\n"
        elif h["role"] == "assistant" and h["content"] is None:
            tool_info = ""
            for tool_call in h["tool_calls"]:
                tool_info += f"Tool: {tool_call.function.name} input: {tool_call.function.arguments}\n"
            context += tool_info
        elif h["role"] == "tool" and h["content"]:
            context += f"Tool: {h['name']} output: {h['content']}\n"

    memory = experimental_memory.load()
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                context=context,
                query=query,
                available_tools_str=available_tools_str,
                thought=thought,
                memory=memory,
            ),
        }
    ]
    return messages


def get_reasoning_messages(
    history: list[dict[str, Any]],
    available_tools_str: str,
    experimental_memory: ExperimentalMemory,
) -> list[dict[str, Any]]:
    query = history[-1]["content"]

    # Unify the history into a single string variable `context`
    context = ""
    for h in history:
        if h["role"] == "user":
            context += f"User: {h['content']}\n"
        elif (
            h["role"] == "assistant"
            and h["content"]
            and not h["content"].startswith("Thought:")
        ):
            context += f"AI Agent: {h['content']}\n"
        elif h["role"] == "assistant" and h["content"] is None:  # input
            tool_info = ""
            for tool_call in h["tool_calls"]:
                tool_info += f"Tool: {tool_call.function.name} input: {tool_call.function.arguments}\n"
            context += tool_info
        elif h["role"] == "tool" and h["content"]:  # output
            context += f"Tool: {h['name']} output: {h['content']}\n"

    memory = experimental_memory.load()
    messages = [
        {
            "role": "system",
            "content": REASONING_PROMPT.format(
                context=context,
                query=query,
                available_tools_str=available_tools_str,
                memory=memory,
            ),
        }
    ]
    return messages
