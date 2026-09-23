import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Always load the .env file from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(
    PROJECT_ROOT / ".env",
    override=True,
)


@dataclass
class Config:
    """Central application configuration."""

    # Active provider
    ai_provider: str = os.getenv(
        "AI_PROVIDER",
        "openrouter",
    ).strip().lower()

    # OpenRouter
    openrouter_api_key: str | None = os.getenv(
        "OPENROUTER_API_KEY"
    )

    openrouter_model: str | None = os.getenv(
        "OPENROUTER_MODEL"
    )

    # UnoRouter
    unorouter_api_key: str | None = os.getenv(
        "UNOROUTER_API_KEY"
    )

    unorouter_model: str | None = os.getenv(
        "UNOROUTER_MODEL"
    )

    @property
    def has_openrouter_key(self) -> bool:
        return bool(self.openrouter_api_key)

    @property
    def has_openrouter_model(self) -> bool:
        return bool(self.openrouter_model)

    @property
    def has_unorouter_key(self) -> bool:
        return bool(self.unorouter_api_key)

    @property
    def has_unorouter_model(self) -> bool:
        return bool(self.unorouter_model)


config = Config()
