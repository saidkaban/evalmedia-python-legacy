# Agent Integration

evalmedia is designed to be called by AI agents as a tool. It ships ready-made tool schemas for OpenAI and Anthropic function calling.

## Tool Schemas

### OpenAI Function Calling

```python
from evalmedia.integrations import openai_tool_schema

# Get the tool definition
tools = [openai_tool_schema()]

# Pass to OpenAI
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=tools,
)
```

### Anthropic Tool Use

```python
from evalmedia.integrations import anthropic_tool_schema

# Get the tool definition
tools = [anthropic_tool_schema()]

# Pass to Anthropic
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=messages,
    tools=tools,
)
```

## Executing Tool Calls

When an agent calls the `evaluate_image` tool, use `execute_tool_call` to run it:

```python
from evalmedia.integrations.openai_tools import execute_tool_call

# Parse the tool call arguments from the agent's response
arguments = {"image_url": "output.png", "prompt": "a cat", "rubric": "general_quality"}

# Execute and get structured result
result = execute_tool_call(arguments)
# Returns a dict with passed, overall_score, check_results, suggestions
```

## Agent Workflow Pattern

A typical generate-evaluate-retry loop:

```python
import asyncio
from evalmedia import ImageEval
from evalmedia.rubrics import Portrait

async def generate_with_quality_gate(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        # 1. Generate image (your generation code here)
        image = await generate_image(prompt)

        # 2. Evaluate
        result = await ImageEval.arun(
            image=image,
            prompt=prompt,
            rubric=Portrait(),
        )

        # 3. Ship or retry
        if result.passed:
            return image, result

        # 4. Use suggestions to adjust
        for suggestion in result.suggestions:
            print(f"Issue: {suggestion}")
        # Modify prompt based on suggestions...

    return image, result  # return best effort
```

## EvalResult for Agents

The `EvalResult.to_dict()` method returns agent-friendly JSON:

```json
{
  "passed": false,
  "overall_score": 0.62,
  "check_results": [
    {
      "name": "face_artifacts",
      "status": "failed",
      "score": 0.3,
      "reasoning": "Extra finger detected on left hand...",
      "confidence": 0.9
    }
  ],
  "suggestions": [
    "[face_artifacts] Extra finger detected on left hand..."
  ],
  "duration_ms": 2340.5,
  "judge_used": "claude"
}
```

The `suggestions` field is key — instead of just "FAIL", agents get actionable guidance on what to fix.
