"""Example: writing a custom check."""

from evalmedia.checks.base import VLMCheck


class BrandColorMatch(VLMCheck):
    """Custom check: does the image use the brand's color palette?"""

    name = "brand_color_match"
    display_name = "Brand Color Match"
    description = "Checks if the image uses the specified brand color palette."
    default_threshold = 0.6

    def __init__(self, palette: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.palette = palette or ["#FF5733", "#1A1A2E"]

    PROMPT_TEMPLATE = """\
Evaluate whether this image predominantly uses the following brand colors:

{colors}

Consider:
1. Are the brand colors prominently featured?
2. Is the overall color scheme consistent with the palette?
3. Do any large areas use colors that clash with the brand palette?

Scoring guide:
- 1.0: Image perfectly matches the brand color palette
- 0.7-0.9: Brand colors are dominant with minor deviations
- 0.4-0.6: Some brand colors present but mixed with off-brand colors
- 0.1-0.3: Brand colors barely present
- 0.0: No brand colors used at all

The generation prompt was: "{prompt}"
"""

    def get_check_prompt(self, prompt: str, **kwargs) -> str:
        colors = ", ".join(self.palette)
        return self.PROMPT_TEMPLATE.format(colors=colors, prompt=prompt)


# Usage:
if __name__ == "__main__":
    from evalmedia import ImageEval
    from evalmedia.rubrics import Rubric, WeightedCheck
    from evalmedia.checks.image import PromptAdherence, AestheticQuality

    # Use the custom check in a rubric
    rubric = Rubric(
        name="branded_content",
        checks=[
            WeightedCheck(check=PromptAdherence(), weight=0.3),
            WeightedCheck(check=AestheticQuality(), weight=0.3),
            WeightedCheck(
                check=BrandColorMatch(palette=["#FF5733", "#1A1A2E", "#E2D1F9"]),
                weight=0.4,
            ),
        ],
        pass_threshold=0.7,
    )

    result = ImageEval.run(
        image="branded_output.png",
        prompt="social media banner for tech startup",
        rubric=rubric,
    )
    print(result.summary())
