# Getting Started

## Installation

```bash
pip install evalmedia
```

Install with a judge backend:

=== "Claude (recommended)"

    ```bash
    pip install evalmedia[claude]
    ```

=== "OpenAI"

    ```bash
    pip install evalmedia[openai]
    ```

=== "Everything"

    ```bash
    pip install evalmedia[all]
    ```

## Configuration

Set your API key via environment variable or code:

=== "Environment variable"

    ```bash
    export EVALMEDIA_ANTHROPIC_API_KEY=sk-ant-...
    # or
    export EVALMEDIA_OPENAI_API_KEY=sk-...
    ```

=== "Python"

    ```python
    import evalmedia

    evalmedia.set_judge("claude", api_key="sk-ant-...")
    # or
    evalmedia.set_judge("openai", api_key="sk-...")
    ```

## Your First Evaluation

### With individual checks

```python
from evalmedia import ImageEval
from evalmedia.checks.image import FaceArtifacts, PromptAdherence, ResolutionAdequacy

result = ImageEval.run(
    image="output.png",
    prompt="a woman holding a coffee cup in a cafe",
    checks=[FaceArtifacts(), PromptAdherence(), ResolutionAdequacy()],
)

print(result.passed)
print(result.overall_score)
print(result.summary())

# Inspect individual checks
for check in result.check_results:
    print(f"  {check.name}: {check.status.value} (score: {check.score})")
    print(f"    {check.reasoning}")
```

### With a rubric

Rubrics are pre-configured sets of weighted checks for specific use cases:

```python
from evalmedia import ImageEval
from evalmedia.rubrics import Portrait

result = ImageEval.run(
    image="headshot.png",
    prompt="professional headshot of a young man",
    rubric=Portrait(),
)

# Rubric computes a weighted overall score
print(f"Score: {result.overall_score:.2f}")
print(f"Passed: {result.passed}")
```

### Async usage

For agent workflows, use the async API:

```python
result = await ImageEval.arun(
    image="output.png",
    prompt="a sunset over mountains",
    rubric=GeneralQuality(),
)
```

## Image Input Formats

evalmedia accepts images in any common format:

```python
# File path
result = ImageEval.run(image="output.png", ...)

# URL
result = ImageEval.run(image="https://example.com/image.png", ...)

# PIL Image
from PIL import Image
img = Image.open("output.png")
result = ImageEval.run(image=img, ...)

# Raw bytes
with open("output.png", "rb") as f:
    result = ImageEval.run(image=f.read(), ...)

# Base64 data URI
result = ImageEval.run(image="data:image/png;base64,iVBOR...", ...)
```

## What's Next?

- [Checks](checks.md) — learn about all 8 built-in checks
- [Rubrics](rubrics.md) — pre-configured check sets and custom rubrics
- [CLI](cli.md) — evaluate images from the command line
- [Agent Integration](agent-integration.md) — use evalmedia in AI agent workflows
