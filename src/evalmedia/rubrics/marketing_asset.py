"""Marketing asset rubric — optimized for text-heavy marketing images."""

from evalmedia.checks.image import (
    AestheticQuality,
    CLIPSimilarity,
    PromptAdherence,
    ResolutionAdequacy,
    TextLegibility,
)
from evalmedia.rubrics.base import Rubric, WeightedCheck


class MarketingAsset(Rubric):
    """Quality rubric optimized for AI-generated marketing assets with text."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="marketing_asset",
            description="Quality evaluation rubric optimized for text-heavy marketing images.",
            checks=[
                WeightedCheck(check=TextLegibility(threshold=0.6), weight=0.30),
                WeightedCheck(check=PromptAdherence(), weight=0.25),
                WeightedCheck(check=AestheticQuality(), weight=0.20),
                WeightedCheck(
                    check=ResolutionAdequacy(min_width=1080, min_height=1080),
                    weight=0.15,
                ),
                WeightedCheck(check=CLIPSimilarity(), weight=0.10),
            ],
            pass_threshold=0.70,
            **kwargs,
        )
