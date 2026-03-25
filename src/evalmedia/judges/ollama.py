"""Ollama judge implementation — local open-source models, no API key required."""

from __future__ import annotations

from PIL import Image

from evalmedia.config import get_config
from evalmedia.image_utils import image_to_base64
from evalmedia.judges._parsing import parse_judge_response
from evalmedia.judges._prompts import JUDGE_SYSTEM_PROMPT
from evalmedia.judges._retry import with_retry
from evalmedia.judges.base import JudgeResponse

_OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"
_OLLAMA_DEFAULT_MODEL = "llama3.2-vision"


class OllamaJudge:
    """Judge that uses locally-running Ollama models — no API key needed."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
    ):
        config = get_config()
        self._model = model or config.default_model_ollama
        self._base_url = base_url or config.ollama_base_url
        self._client = None

    @property
    def name(self) -> str:
        return "ollama"

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "Ollama judge requires the 'openai' package. "
                    "Install with: pip install evalmedia[ollama]"
                )
            self._client = openai.AsyncOpenAI(
                api_key="ollama",  # Ollama doesn't need a real key
                base_url=self._base_url,
            )
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
        """Send image(s) + check prompt to a local Ollama model."""
        client = self._get_client()

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
