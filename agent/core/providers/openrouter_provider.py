from typing import Any

from openai import OpenAI

from agent.config import config
from agent.core.providers.base import BaseProvider


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider using the OpenAI-compatible API."""

    name = "openrouter"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.openrouter_api_key

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is not configured. "
                "Set OPENROUTER_API_KEY in your .env file."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def send(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a complete request to OpenRouter."""

        request: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        if tools:
            request["tools"] = tools

        try:
            response = self.client.chat.completions.create(
                **request
            )

        except Exception as exc:
            raise RuntimeError(
                f"OpenRouter request failed: {exc}"
            ) from exc

        choice = response.choices[0]
        message = choice.message

        return {
            "message": {
                "role": message.role,
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in (message.tool_calls or [])
                ],
            },
            "usage": self._extract_usage(response),
        }

    def stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ):
        """Stream a response from OpenRouter."""

        request: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        if tools:
            request["tools"] = tools

        try:
            response = self.client.chat.completions.create(
                **request
            )

        except Exception as exc:
            raise RuntimeError(
                f"OpenRouter streaming request failed: {exc}"
            ) from exc

        for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                yield delta.content

    @staticmethod
    def _extract_usage(
        response: Any,
    ) -> dict[str, Any]:
        """Extract token usage when the provider returns it."""

        usage = getattr(response, "usage", None)

        if usage is None:
            return {}

        return {
            "prompt_tokens": getattr(
                usage,
                "prompt_tokens",
                None,
            ),
            "completion_tokens": getattr(
                usage,
                "completion_tokens",
                None,
            ),
            "total_tokens": getattr(
                usage,
                "total_tokens",
                None,
            ),
        }
