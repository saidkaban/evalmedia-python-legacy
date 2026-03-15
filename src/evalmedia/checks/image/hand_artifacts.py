"""Check for hand-related artifacts in AI-generated images."""

from evalmedia.checks.base import VLMCheck


class HandArtifacts(VLMCheck):
    """Detects extra/missing fingers, distorted hands, and impossible poses."""

    name = "hand_artifacts"
    display_name = "Hand Artifacts"
    description = "Detects extra/missing fingers, fused digits, distorted hands, and impossible hand poses."
    default_threshold = 0.6

    PROMPT_TEMPLATE = """\
Examine this image for hand-related artifacts commonly produced by AI image generation.

IMPORTANT: For each visible hand, count the fingers carefully.

Look specifically for:
1. Wrong number of fingers (more or fewer than 5 per hand)
2. Fused or merged fingers
3. Extra thumbs or missing thumbs
4. Impossible hand poses or joint angles
5. Hands with distorted proportions
6. Fingers bending in unnatural directions
7. Missing hands where they should be visible (e.g., arms ending abruptly)

If no hands are visible in the image, give a score of 1.0 with confidence 1.0.

Scoring guide:
- 1.0: No hands present OR all hands look anatomically correct
- 0.8-0.9: Very minor imperfections (slightly odd proportions but correct finger count)
- 0.5-0.7: Noticeable issues (slightly wrong finger count or mild distortion)
- 0.2-0.4: Obvious artifacts (clearly wrong finger count, fused fingers)
- 0.0-0.1: Severely distorted hands (grotesque deformities)

The generation prompt was: "{prompt}"
"""

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)
