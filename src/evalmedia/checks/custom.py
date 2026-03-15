"""User-defined evaluation criteria via natural language."""

from __future__ import annotations

from typing import Optional

from evalmedia.checks.base import VLMCheck


class CustomCheck(VLMCheck):
    """A check that evaluates images against user-defined criteria in natural language.

    This is the generic escape hatch — describe what you want to evaluate,
    and evalmedia handles the rest using whatever judge is configured.
    """

    check_type = "vlm"
    display_name = "Custom Check"
    description = "User-defined evaluation criteria in natural language."
    default_threshold = 0.5

    PROMPT_TEMPLATE = """\
You are an expert visual quality evaluator.

Evaluate the following image against this criterion:

CRITERION: "{criteria}"

The image was generated from this prompt: "{prompt}"

Think step-by-step:
1. Carefully examine the image.
2. Consider the criterion above and how well the image satisfies it.
3. Provide your reasoning BEFORE giving a score.

Scoring guide:
- 1.0: Fully satisfies the criterion
- 0.7-0.9: Mostly satisfies, minor issues
- 0.4-0.6: Partially satisfies, notable gaps
- 0.1-0.3: Barely satisfies the criterion
- 0.0: Does not satisfy the criterion at all
"""

    def __init__(
        self,
        name: str,
        criteria: str,
        threshold: Optional[float] = None,
        invert: bool = False,
        judge: Optional[str] = None,
    ):
        if not criteria or not criteria.strip():
            raise ValueError("CustomCheck requires non-empty 'criteria'.")
        if not name or not name.strip():
            raise ValueError("CustomCheck requires a non-empty 'name'.")

        super().__init__(threshold=threshold, judge=judge)
        self.name = name.strip()
        self.criteria = criteria.strip()
        self.invert = invert
        self.display_name = f"Custom: {self.name}"

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(criteria=self.criteria, prompt=prompt)

    def _parse_response(self, response):
        """Convert a JudgeResponse into a CheckResult, respecting invert logic."""
        from evalmedia.core import CheckResult, CheckStatus

        score = response.score
        if self.invert:
            passed = score < self.threshold
        else:
            passed = score >= self.threshold

        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
            passed=passed,
            score=score,
            confidence=response.confidence,
            reasoning=response.reasoning,
            threshold=self.threshold,
            metadata={
                **response.metadata,
                "criteria": self.criteria,
                "invert": self.invert,
            },
        )
