"""Embedding-based image-to-image similarity check."""

from __future__ import annotations

from typing import Optional

from PIL import Image

from evalmedia.checks.base import ClassicalCheck
from evalmedia.core import CheckResult, CheckStatus
from evalmedia.image_utils import ImageInput, load_image
from evalmedia.judges.base import Judge


class ImageSimilarity(ClassicalCheck):
    """Computes embedding cosine similarity between a reference image and a target image.

    Uses CLIP (or optionally DINOv2) to embed both images and compare them,
    providing a fast, deterministic, VLM-free measure of visual similarity.
    Complements the VLM-based StyleConsistency check.
    """

    name = "image_similarity"
    display_name = "Image Similarity"
    description = (
        "Computes embedding-based cosine similarity between a reference image and the generated image."
    )
    default_threshold = 0.75

    def __init__(
        self,
        reference: ImageInput | None = None,
        model_name: str = "ViT-B-32",
        pretrained: str = "openai",
        backend: str = "clip",
        **kwargs: object,
    ):
        super().__init__(**kwargs)
        self.reference = reference
        self.model_name = model_name
        self.pretrained = pretrained
        self.backend = backend
        self._model = None
        self._preprocess = None

    def _load_clip(self) -> None:
        try:
            import open_clip
        except ImportError:
            raise ImportError(
                "ImageSimilarity with CLIP backend requires open-clip-torch. "
                "Install with: pip install evalmedia[classical]"
            )

        import torch

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        model, _, preprocess = open_clip.create_model_and_transforms(
            self.model_name, pretrained=self.pretrained
        )
        self._model = model.to(self._device).eval()
        self._preprocess = preprocess

    def _load_dinov2(self) -> None:
        try:
            import torch
        except ImportError:
            raise ImportError(
                "ImageSimilarity with DINOv2 backend requires torch. "
                "Install with: pip install evalmedia[classical]"
            )

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = torch.hub.load("facebookresearch/dinov2", self.model_name).to(self._device).eval()

        from torchvision import transforms

        self._preprocess = transforms.Compose(
            [
                transforms.Resize(256, interpolation=transforms.InterpolationMode.BICUBIC),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def _load_model(self) -> None:
        if self.backend == "dinov2":
            self._load_dinov2()
        else:
            self._load_clip()

    def _encode_image(self, img: Image.Image):
        import torch

        image_input = self._preprocess(img).unsqueeze(0).to(self._device)
        with torch.no_grad():
            if self.backend == "dinov2":
                features = self._model(image_input)
            else:
                features = self._model.encode_image(image_input)
            features = features / features.norm(dim=-1, keepdim=True)
        return features

    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Optional[Judge] = None,
    ) -> CheckResult:
        """Compute embedding cosine similarity between the reference and target image."""
        if self.reference is None:
            return CheckResult(
                name=self.name,
                status=CheckStatus.SKIPPED,
                reasoning=(
                    "No reference image provided. "
                    "Provide a reference via ImageSimilarity(reference=...)."
                ),
            )

        if self._model is None:
            self._load_model()

        import torch

        ref_image = await load_image(self.reference)

        ref_features = self._encode_image(ref_image)
        target_features = self._encode_image(image)

        similarity = (ref_features @ target_features.T).item()
        score = max(0.0, min(1.0, similarity))
        passed = score >= self.threshold

        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
            passed=passed,
            score=score,
            confidence=1.0,
            reasoning=(
                f"Image embedding cosine similarity: {similarity:.4f} "
                f"(threshold: {self.threshold}, backend: {self.backend})"
            ),
            metadata={
                "cosine_similarity": similarity,
                "backend": self.backend,
                "model": self.model_name,
            },
            threshold=self.threshold,
        )
