"""Portrait rubric — optimized for face/headshot generation."""

from evalmedia.checks.image import (
    AestheticQuality,
    FaceArtifacts,
    HandArtifacts,
    PromptAdherence,
    ResolutionAdequacy,
)
from evalmedia.rubrics.base import Rubric, WeightedCheck


class Portrait(Rubric):
    """Quality rubric optimized for AI-generated portraits and headshots."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="portrait",
            description="Quality evaluation rubric optimized for AI-generated portraits and headshots.",
            checks=[
                WeightedCheck(check=FaceArtifacts(threshold=0.7), weight=0.30),
                WeightedCheck(check=PromptAdherence(), weight=0.20),
                WeightedCheck(check=AestheticQuality(), weight=0.20),
                WeightedCheck(check=HandArtifacts(), weight=0.15),
                WeightedCheck(check=ResolutionAdequacy(min_width=1024, min_height=1024), weight=0.15),
            ],
            pass_threshold=0.70,
            **kwargs,
        )
