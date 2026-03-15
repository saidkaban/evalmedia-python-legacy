"""Check for style consistency against a reference image."""

from __future__ import annotations

from typing import Optional

from PIL import Image

from evalmedia.checks.base import VLMCheck
from evalmedia.core import CheckResult, CheckStatus
from evalmedia.image_utils import ImageInput, load_image
from evalmedia.judges.base import Judge


class StyleConsistency(VLMCheck):
    """Evaluates whether the image matches the style of a reference image."""

    name = "style_consistency"
    display_name = "Style Consistency"
    description = "Evaluates whether the image matches the style of a provided reference image."
    default_threshold = 0.5

    PROMPT_TEMPLATE = """\
You are shown two images. The FIRST image is the reference (the style target). The SECOND image is the generated output to evaluate.

Evaluate how well the second image matches the style of the first image.

Consider:
1. **Color palette**: Do both images use similar colors and tones?
2. **Artistic style**: Do they share the same rendering technique (photorealistic, cartoon, watercolor, etc.)?
3. **Texture and detail level**: Is the level of detail consistent?
4. **Mood and atmosphere**: Do they convey a similar feeling?
5. **Visual consistency**: Would a viewer consider these from the same "series" or "collection"?

Scoring guide:
- 1.0: Perfect style match — indistinguishable in style from the reference
- 0.7-0.9: Strong match — clearly the same style family with minor differences
- 0.4-0.6: Moderate match — some stylistic similarities but noticeable differences
- 0.1-0.3: Weak match — different styles with only vague similarities
- 0.0: Complete mismatch — entirely different styles

The generation prompt was: "{prompt}"
"""

    def __init__(
        self,
        reference: ImageInput | None = None,
        **kwargs: object,
    ):
        super().__init__(**kwargs)
        self.reference = reference

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)

    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Optional[Judge] = None,
    ) -> CheckResult:
        """Evaluate style consistency — requires a reference image."""
        if self.reference is None:
            return CheckResult(
                name=self.name,
                status=CheckStatus.SKIPPED,
                reasoning="No reference image provided. Provide a reference via StyleConsistency(reference=...).",
            )

        if judge is None:
            from evalmedia.judges import get_judge

            judge_name = self._judge_override or "claude"
            judge = get_judge(judge_name)

        ref_image = await load_image(self.reference)
        check_prompt = self.get_check_prompt(prompt)

        # Send both images: reference first, then target
        response = await judge.evaluate(
            image=[ref_image, image],
            prompt=prompt,
            check_prompt=check_prompt,
        )
        return self._parse_response(response)
