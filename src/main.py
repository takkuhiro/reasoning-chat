import json
import logging
from typing import Any

import chainlit as cl
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from src.common import get_main_messages, get_reasoning_messages
from src.config import get_settings
from src.initialization import initialize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client, memory, tools_instances, tools, available_tools = initialize()

settings = get_settings()


@cl.step(type="tool")
async def call_tool(
    tool_call_id: str,
    name: str,
    inputs: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    logger.info(
        f"call_tool input: {tool_call_id=}, {name=}, {inputs=}, {messages=}"
    )
    current_step = cl.context.current_step
    current_step.name = name
    current_step.input = inputs

    try:
        arguments: dict[str, Any] = json.loads(inputs)
        function_to_call = available_tools[name]["run"]
        function_args_keys: list[str] = available_tools[name]["args"]
        function_response = function_to_call(
            **{arg: arguments.get(arg) for arg in function_args_keys}
        )
    except Exception as e:
        logger.error(f"call_tool error: {e}")
        return {
            "role": "tool",
            "name": name,
            "content": "Failed to execute the tool.",
            "tool_call_id": tool_call_id,
        }

    logger.info(
        f"call_tool output: {name=}, {arguments=}, {function_response=}"
    )

    current_step.output = function_response
    current_step.language = "json"

    tool_output = {
        "role": "tool",
        "name": name,
        "content": function_response,
        "tool_call_id": tool_call_id,
    }
    return tool_output


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("history", [])

    available_tools_str = "\n".join(
        [
            f"- {instance.name}: {instance.description}"
            for instance in tools_instances
        ]
    )
    cl.user_session.set("available_tools_str", available_tools_str)

    await cl.Message(
        content=f"I'm an AI agent!\n** Available tools **\n{available_tools_str}",
    ).send()


@cl.step(type="llm")
async def reasoning_step(history: list[dict[str, Any]]) -> None:
    """
    Step to think about a solution.
    The result is added to history.

    Args:
        history (list[dict[str, Any]]): The entire conversation history between the user and the AI agent
    """
    available_tools = cl.user_session.get("available_tools")
    messages = get_reasoning_messages(history, available_tools, memory)

    current_step = cl.context.current_step

    async for content, _ in client.stream_completion(
        messages=messages, tools=tools, settings=settings
    ):
        if content:
            await current_step.stream_token(content)

    logger.info(f"Reasoning output: {current_step.output}")
    history.append({"role": "assistant", "content": current_step.output})
    cl.user_session.set("history", history)
    cl.user_session.set("history", history)


@cl.on_message
async def main(msg: cl.Message) -> None:
    if msg.content == "":
        await cl.Message(content="Please enter a message.").send()
        return

    content = msg.content
    if msg.elements:
        content += "\n--- Attached files ---\n"
        for file in msg.elements:
            content += f"- {file.path} ({file.mime})\n"
    logger.info(f"main user input: {content}")

    history: list[dict[str, Any]] = cl.user_session.get("history")
    history.append({"role": "user", "content": content})

    # Recursively reasoning, using tools and streaming response
    async def _stream_response(messages: list[dict[str, Any]]) -> None:
        # 1. Reasoning step
        await reasoning_step(history)

        # 2. Streaming response with tool calls
        available_tools = cl.user_session.get("available_tools")
        thought = cl.context.current_step.output
        messages = get_main_messages(history, available_tools, thought, memory)
        logger.info(f"main messages: {messages}")

        response = cl.Message(content="")
        tool_calls_buffer: list[ChatCompletionMessageToolCall] = []

        logger.info(f"main tools: {tools}")
        async for content, tool_calls in client.stream_completion(
            messages=messages, tools=tools, settings=settings
        ):
            if content:
                if not response.content:
                    await response.send()
                await response.stream_token(content)

            if tool_calls:
                for tool_call in tool_calls:
                    if tool_call.index >= len(tool_calls_buffer):
                        tool_calls_buffer.append(
                            ChatCompletionMessageToolCall(
                                id=tool_call.id,  # type: ignore
                                function=Function(
                                    name=tool_call.function.name,  # type: ignore
                                    arguments=tool_call.function.arguments,  # type: ignore
                                ),
                                type="function",
                            )
                        )
                    else:
                        if tool_call.function.name:  # type: ignore
                            tool_calls_buffer[
                                tool_call.index
                            ].function.name = tool_call.function.name  # type: ignore
                        if tool_call.function.arguments:  # type: ignore
                            tool_calls_buffer[
                                tool_call.index
                            ].function.arguments += (
                                tool_call.function.arguments  # type: ignore
                            )

        # 3. If there is a tool call, add it to history and execute it
        if tool_calls_buffer:
            logger.info(f"main tool calling: {tool_calls_buffer=}")
            tool_input = {
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls_buffer,
            }
            messages.append(tool_input)
            history.append(tool_input)

            for tool_call in tool_calls_buffer:  # type: ignore
                tool_output = await call_tool(
                    tool_call.id,  # type: ignore
                    tool_call.function.name,  # type: ignore
                    tool_call.function.arguments,  # type: ignore
                    messages,
                )
                messages.append(tool_output)
                history.append(tool_output)
            cl.user_session.set("history", history)

            # If there is a tool call, recursively execute reasoning step
            await _stream_response(messages)
        else:
            # If there is no tool call, add the final response to history
            logger.info(f"Response: {response.content}")
            history.append({"role": "assistant", "content": response.content})
            cl.user_session.set("history", history)
            await response.update()

    # Start the first processing
    await _stream_response(messages=[])
