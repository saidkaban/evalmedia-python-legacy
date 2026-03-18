"""Core data models for evalmedia."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    """Status of a check evaluation."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class CheckResult(BaseModel):
    """Result of a single check evaluation."""

    name: str
    status: CheckStatus
    passed: bool | None = None
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    threshold: float = 0.5
    duration_ms: float = 0.0
    error: str | None = None


class EvalResult(BaseModel):
    """Result of a full evaluation (multiple checks)."""

    passed: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    check_results: list[CheckResult] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    judge_used: str = ""
    image_source: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict suitable for agent consumption."""
        return self.model_dump()

    def summary(self) -> str:
        """Return a human-readable one-line summary."""
        total = len(self.check_results)
        passed_count = sum(1 for r in self.check_results if r.status == CheckStatus.PASSED)
        status = "PASS" if self.passed else "FAIL"

        failed_names = [r.name for r in self.check_results if r.status == CheckStatus.FAILED]
        detail = ""
        if failed_names:
            detail = f" Failed: {', '.join(failed_names)}."

        return (
            f"{status} — {passed_count}/{total} checks passed "
            f"(score: {self.overall_score:.2f}).{detail}"
        )


class CompareResult(BaseModel):
    """Result of comparing multiple images."""

    rankings: list[tuple[str, EvalResult]] = Field(default_factory=list)
    prompt: str = ""
    rubric_name: str = ""

    def best(self) -> tuple[str, EvalResult]:
        """Return the top-ranked (label, result) pair."""
        if not self.rankings:
            raise ValueError("No rankings available")
        return self.rankings[0]
