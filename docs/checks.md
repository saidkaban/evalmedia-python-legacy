# Checks

A **check** is the fundamental unit of evaluation. Each check answers a specific, bounded question about an image and returns a structured `CheckResult`.

## Available Checks

### VLM-Powered Checks

These use a vision-language model (Claude or GPT-4.1) as a judge.

#### PromptAdherence

Does the image match what was asked for?

```python
from evalmedia.checks.image import PromptAdherence

check = PromptAdherence(threshold=0.6)  # default threshold
result = check.run(image="output.png", prompt="a cat on a table")
```

Evaluates: subject presence, spatial relationships, colors, styles, contradictions.

#### FaceArtifacts

Detects distorted faces, wrong eye count, melted features.

```python
from evalmedia.checks.image import FaceArtifacts

check = FaceArtifacts(threshold=0.6)
result = check.run(image="portrait.png", prompt="portrait of a woman")
```

Looks for: wrong eye count, asymmetry, melted regions, uncanny valley effects. Returns score of 1.0 if no faces are present.

#### HandArtifacts

Detects extra/missing fingers, distorted hands.

```python
from evalmedia.checks.image import HandArtifacts

check = HandArtifacts(threshold=0.6)
result = check.run(image="output.png", prompt="person waving")
```

Specifically counts fingers on each visible hand. Returns 1.0 if no hands present.

#### TextLegibility

Is text in the image readable and correctly spelled?

```python
from evalmedia.checks.image import TextLegibility

check = TextLegibility(threshold=0.5)
result = check.run(image="banner.png", prompt="sale banner with 50% off")
```

Identifies all text elements, checks spelling and readability. Returns 1.0 if no text present.

#### AestheticQuality

Evaluates composition, lighting, color harmony, and overall appeal.

```python
from evalmedia.checks.image import AestheticQuality

check = AestheticQuality(threshold=0.5)
result = check.run(image="output.png", prompt="landscape photo")
```

#### StyleConsistency

Does the image match a reference image's style?

```python
from evalmedia.checks.image import StyleConsistency

check = StyleConsistency(reference="reference.png", threshold=0.5)
result = check.run(image="output.png", prompt="portrait in oil painting style")
```

!!! note
    Requires a `reference` image. Returns `SKIPPED` if no reference is provided.

### Classical Checks

These use traditional CV/ML metrics — no VLM judge needed.

#### CLIPSimilarity

CLIP cosine similarity between the prompt text and image.

```python
from evalmedia.checks.image import CLIPSimilarity

check = CLIPSimilarity(threshold=0.25, model_name="ViT-B-32")
result = check.run(image="output.png", prompt="a red car")
```

!!! info
    Requires `pip install evalmedia[classical]` for PyTorch and open-clip-torch.

#### ResolutionAdequacy

Is the image resolution sufficient?

```python
from evalmedia.checks.image import ResolutionAdequacy

# Custom dimensions
check = ResolutionAdequacy(min_width=1024, min_height=1024)

# Or use a preset
check = ResolutionAdequacy(target="hd")     # 1920x1080
check = ResolutionAdequacy(target="4k")     # 3840x2160
check = ResolutionAdequacy(target="social") # 1080x1080
```

No API key needed — pure PIL-based check.

## CheckResult

Every check returns a `CheckResult`:

```python
result = check.run(image="output.png", prompt="...")

result.name          # "face_artifacts"
result.status        # CheckStatus.PASSED | FAILED | ERROR | SKIPPED
result.passed        # True/False
result.score         # 0.0 to 1.0
result.confidence    # 0.0 to 1.0 (judge's confidence)
result.reasoning     # "No facial artifacts detected..."
result.metadata      # check-specific extra data
result.threshold     # the threshold used for pass/fail
result.duration_ms   # how long the check took
```

## Custom Thresholds

Every check accepts a `threshold` parameter. The check passes if `score >= threshold`:

```python
# Strict — only pass if score is very high
check = FaceArtifacts(threshold=0.9)

# Lenient — pass even with some issues
check = FaceArtifacts(threshold=0.3)
```

## Writing a Custom Check

```python
from evalmedia.checks.base import VLMCheck

class BrandColorMatch(VLMCheck):
    name = "brand_color_match"
    display_name = "Brand Color Match"
    description = "Checks if the image uses brand colors."
    default_threshold = 0.6

    PROMPT_TEMPLATE = """
    Does this image use these brand colors: {colors}?
    The generation prompt was: "{prompt}"
    """

    def __init__(self, palette: list[str], **kwargs):
        super().__init__(**kwargs)
        self.palette = palette

    def get_check_prompt(self, prompt: str, **kwargs) -> str:
        return self.PROMPT_TEMPLATE.format(
            colors=", ".join(self.palette),
            prompt=prompt,
        )
```
