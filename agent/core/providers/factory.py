from agent.config import config
from agent.core.providers.base import BaseProvider
from agent.core.providers.openrouter_provider import (
    OpenRouterProvider,
)
from agent.core.providers.unorouter_provider import (
    UnoRouterProvider,
)


def create_provider(
    provider_name: str | None = None,
) -> BaseProvider:
    """Create the configured AI provider."""

    name = (
        provider_name
        or config.ai_provider
    ).lower().strip()

    if name == "openrouter":
        return OpenRouterProvider()

    if name == "unorouter":
        return UnoRouterProvider()

    raise ValueError(
        f"Unsupported AI provider: {name}. "
        "Supported providers: openrouter, unorouter."
    )
