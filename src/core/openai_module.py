import logging
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDeltaToolCall,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatOpenAIClient:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def stream_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list | None = None,
        settings: dict | None = None,
    ) -> AsyncGenerator[
        tuple[str | None, list[ChoiceDeltaToolCall] | None], None
    ]:
        """
        Streams the completion of a chat message.

        Args:
            messages: Message history
            tools: List of available tools
            settings: OpenAI API settings

        Yields:
            tuple[content, tool_call]: A combination of content and tool call
        """
        stream: ChatCompletion | AsyncStream[ChatCompletionChunk]
        current_settings = settings or {}
        if tools:
            current_settings["tools"] = tools
        try:
            stream = await self.client.chat.completions.create(  # type: ignore
                messages=messages,  # type: ignore
                stream=True,
                **current_settings,
            )
            if isinstance(stream, ChatCompletion):
                raise ValueError("Expected AsyncStream but got ChatCompletion")
            async_stream: AsyncStream[ChatCompletionChunk] = stream
        except Exception as e:
            logger.error(f"Failed to create chat completion: {e}")
            return

        async for part in async_stream:
            if not part.choices:
                continue
            new_delta = part.choices[0].delta
            tool_calls = part.choices[0].delta.tool_calls
            if new_delta.content or tool_calls:
                yield new_delta.content, tool_calls
