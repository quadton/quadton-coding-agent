from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    """Central application configuration."""

    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str | None = os.getenv("OPENROUTER_MODEL")

    @property
    def has_openrouter_key(self) -> bool:
        """Return True when an OpenRouter API key is configured."""
        return bool(self.openrouter_api_key)

    @property
    def has_openrouter_model(self) -> bool:
        """Return True when an OpenRouter model is configured."""
        return bool(self.openrouter_model)


config = Config()
