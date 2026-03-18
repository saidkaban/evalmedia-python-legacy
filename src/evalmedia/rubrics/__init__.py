"""Rubric registry and built-in rubrics."""

from __future__ import annotations

from pathlib import Path

from evalmedia.rubrics.base import Rubric, WeightedCheck
from evalmedia.rubrics.general_quality import GeneralQuality
from evalmedia.rubrics.marketing_asset import MarketingAsset
from evalmedia.rubrics.portrait import Portrait

__all__ = [
    "GeneralQuality",
    "MarketingAsset",
    "Portrait",
    "Rubric",
    "WeightedCheck",
    "load_rubric",
]

RUBRIC_REGISTRY: dict[str, type[Rubric]] = {
    "general_quality": GeneralQuality,
    "portrait": Portrait,
    "marketing_asset": MarketingAsset,
}


def load_rubric(name_or_path: str, **kwargs: object) -> Rubric:
    """Load a rubric by name or from a YAML file path.

    Args:
        name_or_path: Built-in rubric name (e.g. "portrait") or path to a YAML file.
        **kwargs: Passed to the rubric constructor.
    """
    # Check built-in registry first
    if name_or_path in RUBRIC_REGISTRY:
        return RUBRIC_REGISTRY[name_or_path](**kwargs)

    # Try as YAML file path
    path = Path(name_or_path)
    if path.exists() and path.suffix in (".yaml", ".yml"):
        return Rubric.from_yaml(path)

    # Try built-in templates
    template_dir = Path(__file__).parent / "templates"
    template_path = template_dir / f"{name_or_path}.yaml"
    if template_path.exists():
        return Rubric.from_yaml(template_path)

    available = ", ".join(RUBRIC_REGISTRY.keys())
    raise ValueError(f"Rubric '{name_or_path}' not found. Built-in rubrics: {available}")
