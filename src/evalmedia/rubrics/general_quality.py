"""General quality rubric — balanced default for most use cases."""

from evalmedia.checks.image import (
    AestheticQuality,
    CLIPSimilarity,
    FaceArtifacts,
    HandArtifacts,
    PromptAdherence,
    ResolutionAdequacy,
    TextLegibility,
)
from evalmedia.rubrics.base import Rubric, WeightedCheck


class GeneralQuality(Rubric):
    """Balanced quality rubric for general image evaluation."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="general_quality",
            description="Balanced quality evaluation rubric for general AI-generated images.",
            checks=[
                WeightedCheck(check=PromptAdherence(), weight=0.25),
                WeightedCheck(check=AestheticQuality(), weight=0.20),
                WeightedCheck(check=FaceArtifacts(), weight=0.15),
                WeightedCheck(check=HandArtifacts(), weight=0.15),
                WeightedCheck(check=TextLegibility(), weight=0.10),
                WeightedCheck(check=ResolutionAdequacy(), weight=0.10),
                WeightedCheck(check=CLIPSimilarity(), weight=0.05),
            ],
            pass_threshold=0.65,
            **kwargs,
        )
