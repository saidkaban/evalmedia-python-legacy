"""Claude judge implementation using the Anthropic API."""

from __future__ import annotations

from typing import Union

from PIL import Image

from evalmedia.config import get_config
from evalmedia.image_utils import image_to_base64
from evalmedia.judges._parsing import parse_judge_response
from evalmedia.judges._prompts import JUDGE_SYSTEM_PROMPT
from evalmedia.judges._retry import with_retry
from evalmedia.judges.base import JudgeResponse


class ClaudeJudge:
    """Judge implementation using Claude via the Anthropic API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        config = get_config()
        self._api_key = api_key or config.anthropic_api_key
        self._model = model or config.default_model_claude
        self._client = None

    @property
    def name(self) -> str:
        return "claude"

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "Claude judge requires the 'anthropic' package. "
                    "Install with: pip install evalmedia[claude]"
                )
            if not self._api_key:
                raise ValueError(
                    "Anthropic API key required. Set EVALMEDIA_ANTHROPIC_API_KEY "
                    "environment variable or pass api_key to ClaudeJudge()."
                )
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._client

    async def evaluate(
        self,
        image: Union[Image.Image, list[Image.Image]],
        prompt: str,
        check_prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> JudgeResponse:
        """Send image(s) + check prompt to Claude and return structured response."""
        client = self._get_client()

        # Build image content blocks
        images = image if isinstance(image, list) else [image]
        content: list[dict] = []
        for img in images:
            b64 = image_to_base64(img, fmt="PNG")
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64,
                    },
                }
            )

        content.append({"type": "text", "text": check_prompt})

        async def _call():
            response = await client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=JUDGE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": content}],
            )
            raw_text = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
            return parse_judge_response(
                raw_output=raw_text,
                model=self._model,
                usage=usage,
            )

        config = get_config()
        return await with_retry(
            _call,
            max_retries=config.max_retries,
        )
