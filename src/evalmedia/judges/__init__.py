"""Judge registry and factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from evalmedia.judges.base import Judge, JudgeResponse

if TYPE_CHECKING:
    pass

__all__ = ["Judge", "JudgeResponse", "get_judge", "register_judge"]

_JUDGE_REGISTRY: dict[str, type] = {}
_defaults_registered = False


def register_judge(name: str, judge_class: type) -> None:
    """Register a judge class by name."""
    _JUDGE_REGISTRY[name] = judge_class


def _register_defaults() -> None:
    """Lazily register built-in judges (only if their SDK is installed)."""
    global _defaults_registered
    if _defaults_registered:
        return
    _defaults_registered = True

    try:
        from evalmedia.judges.claude import ClaudeJudge

        register_judge("claude", ClaudeJudge)
    except ImportError:
        pass

    try:
        from evalmedia.judges.openai import OpenAIJudge

        register_judge("openai", OpenAIJudge)
    except ImportError:
        pass

    try:
        from evalmedia.judges.openrouter import OpenRouterJudge

        register_judge("openrouter", OpenRouterJudge)
    except ImportError:
        pass


def get_judge(name: str, **kwargs: object) -> Judge:
    """Get a judge instance by name.

    Args:
        name: Registered judge name (e.g. "claude", "openai").
        **kwargs: Passed to the judge constructor.

    Raises:
        ValueError: If the judge name is not registered.
    """
    _register_defaults()

    if name not in _JUDGE_REGISTRY:
        available = ", ".join(_JUDGE_REGISTRY.keys()) or "(none installed)"
        install_hint = ""
        if name == "claude":
            install_hint = " Install with: pip install evalmedia[claude]"
        elif name in ("openai", "openrouter"):
            install_hint = " Install with: pip install evalmedia[openai]"
        raise ValueError(
            f"Judge '{name}' is not available. Installed judges: {available}.{install_hint}"
        )

    judge_instance: Judge = _JUDGE_REGISTRY[name](**kwargs)
    return judge_instance
