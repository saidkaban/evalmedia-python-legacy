"""Check registry and discovery."""

from __future__ import annotations

from evalmedia.checks.base import BaseCheck, ClassicalCheck, VLMCheck

__all__ = ["BaseCheck", "ClassicalCheck", "VLMCheck", "get_check", "list_checks"]

CHECK_REGISTRY: dict[str, type[BaseCheck]] = {}

_image_checks_registered = False


def _register_image_checks() -> None:
    """Lazily register all built-in image checks."""
    global _image_checks_registered
    if _image_checks_registered:
        return
    _image_checks_registered = True

    from evalmedia.checks.image import ALL_CHECKS

    for cls in ALL_CHECKS:
        CHECK_REGISTRY[cls.name] = cls


def register_check(check_class: type[BaseCheck]) -> type[BaseCheck]:
    """Register a check class in the global registry."""
    CHECK_REGISTRY[check_class.name] = check_class
    return check_class


def get_check(name: str, **kwargs: object) -> BaseCheck:
    """Instantiate a check by its registered name."""
    _register_image_checks()
    if name not in CHECK_REGISTRY:
        available = ", ".join(CHECK_REGISTRY.keys()) or "(none)"
        raise ValueError(
            f"Check '{name}' not found. Available checks: {available}"
        )
    return CHECK_REGISTRY[name](**kwargs)


def list_checks() -> list[str]:
    """Return all registered check names."""
    _register_image_checks()
    return list(CHECK_REGISTRY.keys())
