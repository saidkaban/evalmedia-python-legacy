"""Rubric base classes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from evalmedia.core import CheckResult, CheckStatus, EvalResult


class WeightedCheck(BaseModel):
    """A check with an associated weight for rubric scoring."""

    check: Any  # BaseCheck — use Any to avoid Pydantic serialization issues
    weight: float = Field(ge=0.0, le=1.0)

    model_config = {"arbitrary_types_allowed": True}


class Rubric(BaseModel):
    """A named collection of weighted checks with a pass/fail threshold."""

    name: str
    description: str = ""
    checks: list[WeightedCheck] = Field(default_factory=list)
    pass_threshold: float = 0.7

    model_config = {"arbitrary_types_allowed": True}

    def compute_result(self, check_results: list[CheckResult]) -> EvalResult:
        """Compute weighted overall score and pass/fail from individual check results."""
        total_weight = sum(wc.weight for wc in self.checks)
        if total_weight == 0:
            return EvalResult(
                passed=False,
                overall_score=0.0,
                check_results=check_results,
            )

        weighted_score = 0.0
        for wc, cr in zip(self.checks, check_results):
            score = cr.score if cr.score is not None else 0.0
            weighted_score += wc.weight * score

        overall_score = weighted_score / total_weight
        passed = overall_score >= self.pass_threshold
        suggestions = self._generate_suggestions(check_results)

        return EvalResult(
            passed=passed,
            overall_score=overall_score,
            check_results=check_results,
            suggestions=suggestions,
        )

    def _generate_suggestions(self, results: list[CheckResult]) -> list[str]:
        """Generate actionable suggestions from failed checks."""
        suggestions: list[str] = []
        for wc, result in zip(self.checks, results):
            if result.status == CheckStatus.FAILED and result.reasoning:
                suggestions.append(f"[{result.name}] {result.reasoning}")
        return suggestions

    @classmethod
    def from_yaml(cls, path: str | Path) -> Rubric:
        """Load a rubric from a YAML file."""
        import yaml

        path = Path(path)
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> Rubric:
        """Create a rubric from a dictionary (e.g., parsed YAML)."""
        from evalmedia.checks import get_check

        weighted_checks = []
        for entry in data.get("checks", []):
            check_name = entry["check"]
            weight = entry.get("weight", 1.0)
            params = entry.get("params", {})
            threshold = entry.get("threshold")
            if threshold is not None:
                params["threshold"] = threshold
            check_instance = get_check(check_name, **params)
            weighted_checks.append(WeightedCheck(check=check_instance, weight=weight))

        return cls(
            name=data.get("name", "custom"),
            description=data.get("description", ""),
            checks=weighted_checks,
            pass_threshold=data.get("pass_threshold", 0.7),
        )
