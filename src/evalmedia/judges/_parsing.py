"""Parse structured responses from VLM judge outputs."""

from __future__ import annotations

import json
import re

from evalmedia.judges.base import JudgeResponse


def parse_judge_response(
    raw_output: str,
    model: str = "",
    usage: dict | None = None,
) -> JudgeResponse:
    """Extract a structured JudgeResponse from raw VLM output.

    Tries in order:
    1. Parse the entire output as JSON
    2. Extract JSON from a fenced code block (```json ... ```)
    3. Extract JSON from the first { ... } block
    4. Regex fallback for score/passed/confidence fields
    """
    usage = usage or {}

    # Strategy 1: entire output is JSON
    data = _try_parse_json(raw_output.strip())
    if data:
        return _build_response(data, raw_output, model, usage)

    # Strategy 2: fenced code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw_output, re.DOTALL)
    if match:
        data = _try_parse_json(match.group(1).strip())
        if data:
            return _build_response(data, raw_output, model, usage)

    # Strategy 3: first { ... } block
    match = re.search(r"\{[^{}]*\}", raw_output, re.DOTALL)
    if match:
        data = _try_parse_json(match.group(0))
        if data:
            return _build_response(data, raw_output, model, usage)

    # Strategy 4: regex fallback
    return _regex_fallback(raw_output, model, usage)


def _try_parse_json(text: str) -> dict | None:
    """Attempt to parse text as JSON, return None on failure."""
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _build_response(
    data: dict,
    raw_output: str,
    model: str,
    usage: dict,
) -> JudgeResponse:
    """Build a JudgeResponse from parsed JSON data."""
    score = float(data.get("score", 0.0))
    score = max(0.0, min(1.0, score))

    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    passed = data.get("passed", score >= 0.5)
    if isinstance(passed, str):
        passed = passed.lower() in ("true", "yes", "1")

    reasoning = data.get("reasoning", "")

    metadata = {k: v for k, v in data.items() if k not in {"score", "passed", "confidence", "reasoning"}}

    return JudgeResponse(
        score=score,
        passed=bool(passed),
        confidence=confidence,
        reasoning=str(reasoning),
        raw_output=raw_output,
        model=model,
        usage=usage,
        metadata=metadata,
    )


def _regex_fallback(
    raw_output: str,
    model: str,
    usage: dict,
) -> JudgeResponse:
    """Last-resort extraction using regex patterns."""
    score = 0.5
    score_match = re.search(r'"?score"?\s*[:=]\s*([\d.]+)', raw_output, re.IGNORECASE)
    if score_match:
        score = max(0.0, min(1.0, float(score_match.group(1))))

    confidence = 0.5
    conf_match = re.search(r'"?confidence"?\s*[:=]\s*([\d.]+)', raw_output, re.IGNORECASE)
    if conf_match:
        confidence = max(0.0, min(1.0, float(conf_match.group(1))))

    passed = score >= 0.5
    pass_match = re.search(r'"?passed"?\s*[:=]\s*(true|false)', raw_output, re.IGNORECASE)
    if pass_match:
        passed = pass_match.group(1).lower() == "true"

    return JudgeResponse(
        score=score,
        passed=passed,
        confidence=confidence,
        reasoning=raw_output[:500],
        raw_output=raw_output,
        model=model,
        usage=usage,
    )
