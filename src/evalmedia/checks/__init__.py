"""Check registry and discovery."""

from __future__ import annotations

from evalmedia.checks.base import BaseCheck, ClassicalCheck, VLMCheck

__all__ = ["BaseCheck", "ClassicalCheck", "VLMCheck", "get_check", "list_checks"]

CHECK_REGISTRY: dict[str, type[BaseCheck]] = {}


def register_check(check_class: type[BaseCheck]) -> type[BaseCheck]:
    """Register a check class in the global registry."""
    CHECK_REGISTRY[check_class.name] = check_class
    return check_class


def get_check(name: str, **kwargs: object) -> BaseCheck:
    """Instantiate a check by its registered name."""
    if name not in CHECK_REGISTRY:
        available = ", ".join(CHECK_REGISTRY.keys()) or "(none)"
        raise ValueError(
            f"Check '{name}' not found. Available checks: {available}"
        )
    return CHECK_REGISTRY[name](**kwargs)


def list_checks() -> list[str]:
    """Return all registered check names."""
    return list(CHECK_REGISTRY.keys())
