"""OpenAI function/tool schema for agent integration."""

from __future__ import annotations

from typing import Any


def openai_tool_schema() -> dict[str, Any]:
    """Return a tool definition compatible with OpenAI's function calling format.

    Usage:
        tools = [openai_tool_schema()]
        response = client.chat.completions.create(..., tools=tools)
    """
    from evalmedia.checks import list_checks
    from evalmedia.rubrics import RUBRIC_REGISTRY

    return {
        "type": "function",
        "function": {
            "name": "evaluate_image",
            "description": (
                "Evaluate the quality of an AI-generated image using structured checks. "
                "Returns detailed scores, pass/fail verdicts, and actionable suggestions."
            ),
            "parameters": {
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
                        "description": "List of specific check names to run. If omitted, uses the rubric.",
                    },
                    "rubric": {
                        "type": "string",
                        "enum": list(RUBRIC_REGISTRY.keys()),
                        "description": "Named rubric for predefined check sets. Defaults to 'general_quality'.",
                    },
                },
                "required": ["image_url"],
            },
        },
    }


def execute_tool_call(arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute an evalmedia tool call and return the result as a dict.

    This bridges agent tool_use calls to actual evalmedia evaluation.

    Args:
        arguments: Parsed arguments from the tool call.

    Returns:
        EvalResult serialized as a dict.
    """
    from evalmedia.checks import get_check
    from evalmedia.eval import ImageEval
    from evalmedia.rubrics import load_rubric

    image = arguments["image_url"]
    prompt = arguments.get("prompt", "")
    check_names = arguments.get("checks")
    rubric_name = arguments.get("rubric")

    checks = None
    rubric = None

    if check_names:
        checks = [get_check(name) for name in check_names]
    elif rubric_name:
        rubric = load_rubric(rubric_name)
    else:
        rubric = load_rubric("general_quality")

    result = ImageEval.run(image=image, prompt=prompt, checks=checks, rubric=rubric)
    return result.to_dict()
