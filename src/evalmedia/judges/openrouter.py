"""OpenRouter judge implementation — OpenAI-compatible gateway for any model."""

from __future__ import annotations

from typing import Union

from PIL import Image

from evalmedia.config import get_config
from evalmedia.image_utils import image_to_base64
from evalmedia.judges._parsing import parse_judge_response
from evalmedia.judges._prompts import JUDGE_SYSTEM_PROMPT
from evalmedia.judges._retry import with_retry
from evalmedia.judges.base import JudgeResponse

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# JSON Schema for structured output via Chat Completions json_schema format.
_JUDGE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "score": {"type": "number"},
        "passed": {"type": "boolean"},
        "confidence": {"type": "number"},
    },
    "required": ["reasoning", "score", "passed", "confidence"],
    "additionalProperties": False,
}


class OpenRouterJudge:
    """Judge that routes to any model via OpenRouter (OpenAI-compatible API)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        config = get_config()
        self._api_key = api_key or config.openrouter_api_key
        self._model = model or config.default_model_openrouter
        self._base_url = base_url or _OPENROUTER_BASE_URL
        self._client = None

    @property
    def name(self) -> str:
        return "openrouter"

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "OpenRouter judge requires the 'openai' package. "
                    "Install with: pip install evalmedia[openai]"
                )
            if not self._api_key:
                raise ValueError(
                    "OpenRouter API key required. Set EVALMEDIA_OPENROUTER_API_KEY "
                    "environment variable or pass api_key to OpenRouterJudge()."
                )
            self._client = openai.AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
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
        """Send image(s) + check prompt via OpenRouter and return structured response."""
        client = self._get_client()

        # Build image content parts (OpenAI Chat Completions format)
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
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "judge_response",
                        "schema": _JUDGE_RESPONSE_SCHEMA,
                        "strict": True,
                    },
                },
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
