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
        response = self.client.chat.completions.create(**request)

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
