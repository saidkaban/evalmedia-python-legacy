"""OpenAI judge implementation using the Responses API with structured output."""

from __future__ import annotations

from PIL import Image

from evalmedia.config import get_config
from evalmedia.image_utils import image_to_base64
from evalmedia.judges._parsing import parse_judge_response
from evalmedia.judges._prompts import JUDGE_SYSTEM_PROMPT
from evalmedia.judges._retry import with_retry
from evalmedia.judges.base import JudgeResponse

# JSON Schema for structured output — guarantees the response matches this shape.
# With strict mode, the model is constrained to produce exactly this structure,
# eliminating the need for fallback parsing strategies.
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


class OpenAIJudge:
    """Judge implementation using GPT-4.1 via the OpenAI Responses API."""

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
        image: Image.Image | list[Image.Image],
        prompt: str,
        check_prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> JudgeResponse:
        """Send image(s) + check prompt to GPT-4.1 and return structured response."""
        client = self._get_client()

        # Build input content parts (Responses API uses input_image / input_text)
        images = image if isinstance(image, list) else [image]
        content: list[dict] = []
        for img in images:
            b64 = image_to_base64(img, fmt="PNG")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{b64}",
                }
            )

        content.append({"type": "input_text", "text": check_prompt})

        async def _call():
            response = await client.responses.create(
                model=self._model,
                instructions=JUDGE_SYSTEM_PROMPT,
                input=[{"role": "user", "content": content}],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "judge_response",
                        "schema": _JUDGE_RESPONSE_SCHEMA,
                        "strict": True,
                    }
                },
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            raw_text = response.output_text
            usage = {}
            if response.usage:
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
