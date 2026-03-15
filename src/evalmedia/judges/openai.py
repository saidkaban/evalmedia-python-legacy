"""OpenAI judge implementation using the OpenAI API."""

from __future__ import annotations

from typing import Union

from PIL import Image

from evalmedia.config import get_config
from evalmedia.image_utils import image_to_base64
from evalmedia.judges._parsing import parse_judge_response
from evalmedia.judges._prompts import JUDGE_SYSTEM_PROMPT
from evalmedia.judges._retry import with_retry
from evalmedia.judges.base import JudgeResponse


class OpenAIJudge:
    """Judge implementation using GPT-4.1 via the OpenAI API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        config = get_config()
        self._api_key = api_key or config.openai_api_key
        self._model = model or config.default_model_openai
        self._client = None

    @property
    def name(self) -> str:
        return "openai"

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenAI judge requires the 'openai' package. "
                    "Install with: pip install evalmedia[openai]"
                )
            if not self._api_key:
                raise ValueError(
                    "OpenAI API key required. Set EVALMEDIA_OPENAI_API_KEY "
                    "environment variable or pass api_key to OpenAIJudge()."
                )
            self._client = openai.AsyncOpenAI(api_key=self._api_key)
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
        """Send image(s) + check prompt to GPT-4.1 and return structured response."""
        client = self._get_client()

        # Build image content parts
        images = image if isinstance(image, list) else [image]
        content: list[dict] = []
        for img in images:
            b64 = image_to_base64(img, fmt="PNG")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                    },
                }
            )

        content.append({"type": "text", "text": check_prompt})

        async def _call():
            response = await client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
            )
            raw_text = response.choices[0].message.content or ""
            usage = {}
            if response.usage:
                usage = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
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
