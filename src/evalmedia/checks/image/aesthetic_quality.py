"""Check for overall aesthetic quality of AI-generated images."""

from evalmedia.checks.base import VLMCheck


class AestheticQuality(VLMCheck):
    """Evaluates composition, lighting, color harmony, and overall visual appeal."""

    name = "aesthetic_quality"
    display_name = "Aesthetic Quality"
    description = "Evaluates composition, lighting, color harmony, and overall visual appeal."
    default_threshold = 0.5

    PROMPT_TEMPLATE = """\
Evaluate the overall aesthetic quality of this image.

Consider these aspects:
1. **Composition**: Is the framing balanced? Is there a clear focal point? Does the layout feel intentional?
2. **Lighting**: Is the lighting natural and appropriate? Are there harsh shadows or blown-out highlights?
3. **Color harmony**: Do the colors work well together? Is the palette pleasing?
4. **Visual clarity**: Is the image sharp where it should be? Is there appropriate depth of field?
5. **Overall appeal**: Would this image look professional and polished to a viewer?

Scoring guide:
- 1.0: Stunning — gallery-quality composition, lighting, and color
- 0.7-0.9: Professional quality — well-composed with good aesthetic choices
- 0.4-0.6: Average — acceptable but unremarkable visual quality
- 0.1-0.3: Below average — poor composition, lighting, or color choices
- 0.0: Very poor — visually unappealing or incoherent

The generation prompt was: "{prompt}"
"""

    def get_check_prompt(self, prompt: str, **kwargs: object) -> str:
        return self.PROMPT_TEMPLATE.format(prompt=prompt)
