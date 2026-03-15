"""Check whether an image matches the generation prompt."""

from evalmedia.checks.base import VLMCheck


class PromptAdherence(VLMCheck):
    """Evaluates whether the generated image matches the intent of the prompt."""

    name = "prompt_adherence"
    display_name = "Prompt Adherence"
    description = "Evaluates whether the generated image matches the intent of the prompt."
    default_threshold = 0.6

    PROMPT_TEMPLATE = """\
Evaluate how well this image matches the following generation prompt:

PROMPT: "{prompt}"

Consider:
1. Are all key subjects/objects mentioned in the prompt present in the image?
2. Are spatial relationships and compositions as described?
3. Are colors, styles, and moods as requested?
4. Is anything present that contradicts the prompt?
5. Does the overall scene match the prompt's intent?

Scoring guide:
- 1.0: Perfect match — every element of the prompt is faithfully represented
- 0.7-0.9: Good match — most elements present, minor deviations
- 0.4-0.6: Partial match — some elements present, significant omissions or changes
- 0.1-0.3: Poor match — image barely relates to the prompt
- 0.0: Complete mismatch — image has nothing to do with the prompt
"""

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)
