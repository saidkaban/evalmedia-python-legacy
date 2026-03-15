"""Check for face-related artifacts in AI-generated images."""

from evalmedia.checks.base import VLMCheck


class FaceArtifacts(VLMCheck):
    """Detects distorted faces, wrong features, and uncanny valley effects."""

    name = "face_artifacts"
    display_name = "Face Artifacts"
    description = "Detects distorted faces, wrong eye count, melted features, and other facial artifacts."
    default_threshold = 0.6

    PROMPT_TEMPLATE = """\
Examine this image for facial artifacts commonly produced by AI image generation.

Look specifically for:
1. Wrong number of eyes (more or fewer than 2 per face)
2. Asymmetric or distorted facial features
3. Melted, blurred, or smeared facial regions
4. Uncanny valley effects (faces that look almost but not quite right)
5. Misaligned or duplicated facial features
6. Unnatural skin texture or coloring on faces
7. Missing or malformed ears, nose, mouth

If no faces are present in the image, give a score of 1.0 with confidence 1.0.

Scoring guide:
- 1.0: No faces present OR all faces look completely natural with no artifacts
- 0.8-0.9: Very minor imperfections that only an expert would notice
- 0.5-0.7: Noticeable artifacts that a casual viewer might spot
- 0.2-0.4: Obvious facial distortions clearly visible to anyone
- 0.0-0.1: Severely distorted or grotesque facial artifacts

The generation prompt was: "{prompt}"
"""

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)
