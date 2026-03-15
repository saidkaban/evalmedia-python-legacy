"""Check whether image resolution meets requirements."""

from __future__ import annotations

from typing import Optional

from PIL import Image

from evalmedia.checks.base import ClassicalCheck
from evalmedia.core import CheckResult, CheckStatus
from evalmedia.judges.base import Judge


class ResolutionAdequacy(ClassicalCheck):
    """Checks whether the image resolution meets minimum requirements."""

    name = "resolution_adequacy"
    display_name = "Resolution Adequacy"
    description = "Checks whether the image resolution is sufficient for the intended use."
    default_threshold = 0.5

    TARGETS: dict[str, tuple[int, int]] = {
        "web": (1024, 1024),
        "print": (3000, 3000),
        "social": (1080, 1080),
        "thumbnail": (256, 256),
        "hd": (1920, 1080),
        "4k": (3840, 2160),
    }

    def __init__(
        self,
        min_width: int = 512,
        min_height: int = 512,
        target: str | None = None,
        **kwargs: object,
    ):
        super().__init__(**kwargs)
        if target and target in self.TARGETS:
            self.min_width, self.min_height = self.TARGETS[target]
        else:
            self.min_width = min_width
            self.min_height = min_height

    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Optional[Judge] = None,
    ) -> CheckResult:
        """Check image dimensions against minimum requirements."""
        w, h = image.size
        width_ratio = min(w / self.min_width, 1.0)
        height_ratio = min(h / self.min_height, 1.0)
        score = (width_ratio + height_ratio) / 2.0
        passed = w >= self.min_width and h >= self.min_height

        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
            passed=passed,
            score=score,
            confidence=1.0,
            reasoning=f"Image is {w}x{h}, minimum required is {self.min_width}x{self.min_height}.",
            metadata={
                "width": w,
                "height": h,
                "min_width": self.min_width,
                "min_height": self.min_height,
            },
            threshold=self.threshold,
        )
