"""CLIP-based similarity check between prompt and image."""

from __future__ import annotations

from PIL import Image

from evalmedia.checks.base import ClassicalCheck
from evalmedia.core import CheckResult, CheckStatus
from evalmedia.judges.base import Judge


class CLIPSimilarity(ClassicalCheck):
    """Computes CLIP cosine similarity between prompt text and image."""

    name = "clip_similarity"
    display_name = "CLIP Similarity"
    description = "Computes CLIP cosine similarity between the prompt text and the image."
    default_threshold = 0.25

    def __init__(
        self,
        model_name: str = "ViT-B-32",
        pretrained: str = "openai",
        threshold: float | None = None,
        judge: str | None = None,
    ):
        super().__init__(threshold=threshold, judge=judge)
        self.model_name = model_name
        self.pretrained = pretrained
        self._model = None
        self._preprocess = None
        self._tokenizer = None

    def _load_model(self) -> None:
        try:
            import open_clip
        except ImportError:
            raise ImportError(
                "CLIPSimilarity requires open-clip-torch. "
                "Install with: pip install evalmedia[classical]"
            )

        import torch

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        model, _, preprocess = open_clip.create_model_and_transforms(
            self.model_name, pretrained=self.pretrained
        )
        self._model = model.to(self._device).eval()
        self._preprocess = preprocess
        self._tokenizer = open_clip.get_tokenizer(self.model_name)

    async def evaluate(
        self,
        image: Image.Image,
        prompt: str,
        judge: Judge | None = None,
    ) -> CheckResult:
        """Compute CLIP cosine similarity between the image and prompt."""
        if self._model is None:
            self._load_model()

        import torch

        assert self._preprocess is not None
        assert self._tokenizer is not None
        assert self._model is not None

        # Preprocess image
        image_input = self._preprocess(image).unsqueeze(0).to(self._device)

        # Tokenize text
        text_input = self._tokenizer([prompt]).to(self._device)

        # Compute embeddings
        with torch.no_grad():
            image_features = self._model.encode_image(image_input)
            text_features = self._model.encode_text(text_input)

            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Cosine similarity
            similarity = (image_features @ text_features.T).item()

        # CLIP similarities are typically in [-1, 1], but usually [0.15, 0.40] for real data
        # Clamp to [0, 1] for our scoring
        score = max(0.0, min(1.0, similarity))
        passed = score >= self.threshold

        return CheckResult(
            name=self.name,
            status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
            passed=passed,
            score=score,
            confidence=1.0,
            reasoning=f"CLIP cosine similarity: {similarity:.4f} (threshold: {self.threshold})",
            metadata={
                "cosine_similarity": similarity,
                "model": self.model_name,
                "pretrained": self.pretrained,
            },
            threshold=self.threshold,
        )
