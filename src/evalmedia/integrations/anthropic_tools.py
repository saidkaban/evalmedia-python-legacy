"""Anthropic tool schema for agent integration."""

from __future__ import annotations

from typing import Any


def anthropic_tool_schema() -> dict[str, Any]:
    """Return a tool definition compatible with Anthropic's tool_use format.

    Usage:
        tools = [anthropic_tool_schema()]
        response = client.messages.create(..., tools=tools)
    """
    from evalmedia.checks import list_checks
    from evalmedia.rubrics import RUBRIC_REGISTRY

    return {
        "name": "evaluate_image",
        "description": (
            "Evaluate the quality of an AI-generated image using structured checks. "
            "Returns detailed scores, pass/fail verdicts, and actionable suggestions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL or file path to the image to evaluate.",
                },
                "prompt": {
                    "type": "string",
                    "description": "The generation prompt used to create the image.",
                },
                "checks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list_checks(),
                    },
                    "description": (
                        "List of specific check names to run. If omitted, uses the rubric."
                    ),
                },
                "rubric": {
                    "type": "string",
                    "enum": list(RUBRIC_REGISTRY.keys()),
                    "description": (
                        "Named rubric for predefined check sets. Defaults to 'general_quality'."
                    ),
                },
            },
            "required": ["image_url"],
        },
    }
