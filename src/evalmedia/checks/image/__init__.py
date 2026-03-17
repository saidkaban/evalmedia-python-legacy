"""Image quality checks."""

from evalmedia.checks.image.aesthetic_quality import AestheticQuality
from evalmedia.checks.image.clip_similarity import CLIPSimilarity
from evalmedia.checks.image.face_artifacts import FaceArtifacts
from evalmedia.checks.image.hand_artifacts import HandArtifacts
from evalmedia.checks.image.image_similarity import ImageSimilarity
from evalmedia.checks.image.prompt_adherence import PromptAdherence
from evalmedia.checks.image.resolution_adequacy import ResolutionAdequacy
from evalmedia.checks.image.style_consistency import StyleConsistency
from evalmedia.checks.image.text_legibility import TextLegibility

ALL_CHECKS: list[type] = [
    PromptAdherence,
    FaceArtifacts,
    HandArtifacts,
    TextLegibility,
    AestheticQuality,
    StyleConsistency,
    CLIPSimilarity,
    ImageSimilarity,
    ResolutionAdequacy,
]

CHECK_REGISTRY: dict[str, type] = {cls.name: cls for cls in ALL_CHECKS}

__all__ = [
    "ALL_CHECKS",
    "CHECK_REGISTRY",
    "AestheticQuality",
    "CLIPSimilarity",
    "FaceArtifacts",
    "HandArtifacts",
    "ImageSimilarity",
    "PromptAdherence",
    "ResolutionAdequacy",
    "StyleConsistency",
    "TextLegibility",
]
