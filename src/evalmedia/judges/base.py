"""Judge protocol and response model."""

from __future__ import annotations

from typing import Any, Protocol, Union, runtime_checkable

from PIL import Image
from pydantic import BaseModel, Field


class JudgeResponse(BaseModel):
    """Structured response from a VLM judge."""

    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    raw_output: str = ""
    model: str = ""
    usage: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Judge(Protocol):
    """Protocol that all judge backends must implement."""

    @property
    def name(self) -> str: ...

    async def evaluate(
        self,
        image: Union[Image.Image, list[Image.Image]],
        prompt: str,
        check_prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> JudgeResponse: ...
