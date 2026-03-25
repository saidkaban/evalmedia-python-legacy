"""Global configuration for evalmedia."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalMediaConfig(BaseSettings):
    """Configuration loaded from environment variables with EVALMEDIA_ prefix."""

    model_config = SettingsConfigDict(env_prefix="EVALMEDIA_")

    default_judge: str = "claude"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    default_model_claude: str = "claude-sonnet-4-20250514"
    default_model_openai: str = "gpt-4.1"
    default_model_openrouter: str = "google/gemini-2.5-flash"
    default_model_ollama: str = "llama3.2-vision"
    ollama_base_url: str = "http://localhost:11434/v1"
    timeout_seconds: float = 60.0
    max_retries: int = 3


_config: EvalMediaConfig | None = None


def get_config() -> EvalMediaConfig:
    """Return the global config singleton, creating it on first call."""
    global _config
    if _config is None:
        _config = EvalMediaConfig()
    return _config


def set_judge(name: str, **kwargs: object) -> None:
    """Set the default judge backend.

    Args:
        name: Judge name (e.g. "claude", "openai").
        **kwargs: Additional config overrides (e.g. api_key).
    """
    config = get_config()
    config.default_judge = name

    if "api_key" in kwargs:
        if name == "claude":
            config.anthropic_api_key = str(kwargs["api_key"])
        elif name == "openai":
            config.openai_api_key = str(kwargs["api_key"])
        elif name == "openrouter":
            config.openrouter_api_key = str(kwargs["api_key"])
        # ollama does not require an API key

    if "model" in kwargs:
        if name == "claude":
            config.default_model_claude = str(kwargs["model"])
        elif name == "openai":
            config.default_model_openai = str(kwargs["model"])
        elif name == "openrouter":
            config.default_model_openrouter = str(kwargs["model"])
        elif name == "ollama":
            config.default_model_ollama = str(kwargs["model"])
