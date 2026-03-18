"""Base classes for checks."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod

from PIL import Image

from evalmedia.core import CheckResult, CheckStatus
from evalmedia.image_utils import ImageInput, load_image
from evalmedia.judges.base import Judge, JudgeResponse


class BaseCheck(ABC):
    """Abstract base class for all checks."""

    name: str = ""
    display_name: str = ""
    description: str = ""
    check_type: str = ""  # "vlm", "classical", "hybrid"
    default_threshold: float = 0.5

    def __init__(
        self,
        threshold: float | None = None,
        judge: str | None = None,
    ):
        self.threshold = threshold if threshold is not None else self.default_threshold
        self._judge_override = judge

    @abstractmethod
    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Judge | None = None,
    ) -> CheckResult:
        """Run the check on an image. Subclasses implement the logic."""
        ...

    def run(self, image: ImageInput, prompt: str = "", **kwargs: object) -> CheckResult:
        """Synchronous entry point."""
        return asyncio.run(self.arun(image, prompt, **kwargs))

    async def arun(
        self,
        image: ImageInput,
        prompt: str = "",
        judge: Judge | None = None,
    ) -> CheckResult:
        """Async entry point that handles image loading and timing."""
        start = time.monotonic()
        pil_image = await load_image(image)
        result = await self.evaluate(pil_image, prompt, judge=judge)
        result.duration_ms = (time.monotonic() - start) * 1000
        return result


class VLMCheck(BaseCheck):
    """Base for checks powered by a vision-language model judge."""

    check_type = "vlm"

    PROMPT_TEMPLATE: str = ""

    @abstractmethod
    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        """Return the VLM evaluation prompt for this check."""
        ...

    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Judge | None = None,
    ) -> CheckResult:
        """Standard VLM evaluation flow: build prompt -> call judge -> parse."""
        if judge is None:
            from evalmedia.judges import get_judge

            judge_name = self._judge_override or "claude"
            judge = get_judge(judge_name)

        check_prompt = self.get_check_prompt(prompt)
        response = await judge.evaluate(image=image, prompt=prompt, check_prompt=check_prompt)
        return self._parse_response(response)

    def _parse_response(self, response: JudgeResponse) -> CheckResult:
        """Convert a JudgeResponse into a CheckResult."""
        passed = response.score >= self.threshold
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
            passed=passed,
            score=response.score,
            confidence=response.confidence,
            reasoning=response.reasoning,
            threshold=self.threshold,
            metadata=response.metadata,
        )


class ClassicalCheck(BaseCheck):
    """Base for checks using traditional CV/ML metrics. No judge needed."""

    check_type = "classical"
