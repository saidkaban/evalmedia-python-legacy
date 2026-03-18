"""Check for text legibility in AI-generated images."""

from evalmedia.checks.base import VLMCheck
from evalmedia.core import CheckResult
from evalmedia.judges.base import JudgeResponse


class TextLegibility(VLMCheck):
    """Evaluates whether text in the image is readable, correctly spelled, and coherent."""

    name = "text_legibility"
    display_name = "Text Legibility"
    description = (
        "Checks if text present in the image is readable, correctly spelled, and makes sense."
    )
    default_threshold = 0.5

    PROMPT_TEMPLATE = """\
Examine this image for any text elements (signs, labels, captions, watermarks, etc.).

For each text element you find:
1. Read it — what does it say?
2. Is it correctly spelled?
3. Is it legible (clear, readable, not blurry or distorted)?
4. Does it make contextual sense in the image?
5. Are any characters garbled, nonsensical, or partially rendered?

If NO text is present in the image, give a score of 1.0 with confidence 1.0.

List each text element you find in your reasoning, noting any issues.

Scoring guide:
- 1.0: No text present OR all text is perfectly legible and correctly spelled
- 0.8-0.9: Text is mostly legible with very minor issues
- 0.5-0.7: Some text is readable but has spelling errors or minor rendering issues
- 0.2-0.4: Text is mostly illegible, garbled, or has major spelling errors
- 0.0-0.1: Text is completely unreadable or nonsensical

The generation prompt was: "{prompt}"
"""

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)

    def _parse_response(self, response: JudgeResponse) -> CheckResult:
        result = super()._parse_response(response)
        # Extract detected text elements from metadata if present
        if "text_elements" in response.metadata:
            result.metadata["detected_text_elements"] = response.metadata["text_elements"]
        return result
