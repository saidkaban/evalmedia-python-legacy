"""Evaluation runner classes."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from typing import TYPE_CHECKING

from PIL import Image

from evalmedia.checks.base import BaseCheck
from evalmedia.config import get_config
from evalmedia.core import CheckResult, CheckStatus, CompareResult, EvalResult
from evalmedia.image_utils import ImageInput, load_image
from evalmedia.judges import get_judge
from evalmedia.judges.base import Judge

if TYPE_CHECKING:
    from evalmedia.rubrics.base import Rubric


async def _run_check_safe(
    check: BaseCheck,
    image: Image.Image,
    prompt: str,
    judge: Judge,
) -> CheckResult:
    """Run a single check with error handling."""
    try:
        return await check.evaluate(image, prompt, judge=judge)
    except Exception as e:
        return CheckResult(
            name=check.name,
            status=CheckStatus.ERROR,
            score=None,
            confidence=None,
            error=str(e),
            reasoning=f"Check failed with error: {e}",
        )


class ImageEval:
    """Run image quality evaluations."""

    @staticmethod
    def run(
        image: ImageInput,
        prompt: str = "",
        checks: list[BaseCheck] | None = None,
        rubric: Rubric | None = None,
        judge: str | None = None,
    ) -> EvalResult:
        """Synchronous evaluation entry point."""
        try:
            asyncio.get_running_loop()
            # Already in an async context
            import nest_asyncio

            nest_asyncio.apply()
        except RuntimeError:
            pass

        return asyncio.run(ImageEval.arun(image, prompt, checks=checks, rubric=rubric, judge=judge))

    @staticmethod
    async def arun(
        image: ImageInput,
        prompt: str = "",
        checks: list[BaseCheck] | None = None,
        rubric: Rubric | None = None,
        judge: str | None = None,
    ) -> EvalResult:
        """Async evaluation entry point. Runs all checks concurrently."""
        start = time.monotonic()

        if checks is None and rubric is None:
            raise ValueError("Either 'checks' or 'rubric' must be provided.")

        # Load image
        pil_image = await load_image(image)

        # Resolve judge
        judge_name = judge or get_config().default_judge
        judge_instance = get_judge(judge_name)

        # Resolve checks
        if rubric is not None:
            check_instances = [wc.check for wc in rubric.checks]
        else:
            check_instances = checks  # type: ignore[assignment]

        # Run all checks concurrently
        tasks = [
            _run_check_safe(check, pil_image, prompt, judge_instance) for check in check_instances
        ]
        check_results = await asyncio.gather(*tasks)

        # Compute overall result
        duration_ms = (time.monotonic() - start) * 1000

        if rubric is not None:
            result = rubric.compute_result(list(check_results))
            result.duration_ms = duration_ms
            result.judge_used = judge_instance.name
            return result

        # Simple aggregation when no rubric
        scores = [r.score for r in check_results if r.score is not None]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        all_passed = all(r.passed for r in check_results if r.passed is not None)
        suggestions = [
            r.reasoning for r in check_results if r.status == CheckStatus.FAILED and r.reasoning
        ]

        return EvalResult(
            passed=all_passed,
            overall_score=overall_score,
            check_results=list(check_results),
            suggestions=suggestions,
            duration_ms=duration_ms,
            judge_used=judge_instance.name,
        )


async def compare(
    images: Sequence[ImageInput],
    prompt: str,
    checks: list[BaseCheck] | None = None,
    rubric: Rubric | None = None,
    judge: str | None = None,
    labels: list[str] | None = None,
) -> CompareResult:
    """Evaluate multiple images and rank them by score."""
    if labels is None:
        labels = [f"image_{i}" for i in range(len(images))]

    tasks = [
        ImageEval.arun(img, prompt, checks=checks, rubric=rubric, judge=judge) for img in images
    ]
    results = await asyncio.gather(*tasks)

    ranked = sorted(
        zip(labels, results),
        key=lambda x: x[1].overall_score,
        reverse=True,
    )

    return CompareResult(
        rankings=list(ranked),
        prompt=prompt,
        rubric_name=rubric.name if rubric else "",
    )
