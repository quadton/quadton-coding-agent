from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    """Central application configuration."""

    ai_provider: str = os.getenv(
        "AI_PROVIDER",
        "openrouter",
    ).lower()

    openrouter_api_key: str | None = os.getenv(
        "OPENROUTER_API_KEY"
    )

    openrouter_model: str | None = os.getenv(
        "OPENROUTER_MODEL"
    )

    unorouter_api_key: str | None = os.getenv(
        "UNOROUTER_API_KEY"
    )

    unorouter_model: str | None = os.getenv(
        "UNOROUTER_MODEL"
    )

    @property
    def has_openrouter_key(self) -> bool:
        """Return True when an OpenRouter API key is configured."""
        return bool(self.openrouter_api_key)

    @property
    def has_openrouter_model(self) -> bool:
        """Return True when an OpenRouter model is configured."""
        return bool(self.openrouter_model)

    @property
    def has_unorouter_key(self) -> bool:
        """Return True when a UnoRouter API key is configured."""
        return bool(self.unorouter_api_key)

    @property
    def has_unorouter_model(self) -> bool:
        """Return True when a UnoRouter model is configured."""
        return bool(self.unorouter_model)
