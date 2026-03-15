# evalmedia

**Open-source framework for evaluating AI-generated media quality.**

Think "DeepEval but for generative media." Structured, actionable quality assessments for AI-generated images — designed for AI agents, not dashboards.

[Website](https://eval.media) | [PyPI](https://pypi.org/project/evalmedia/) | [GitHub](https://github.com/evalmedia/evalmedia)

## Install

```bash
pip install evalmedia
```

With judge backends:

```bash
pip install evalmedia[claude]    # Anthropic Claude
pip install evalmedia[openai]    # OpenAI GPT-4.1
pip install evalmedia[all]       # Everything
```

## Quick Start

### Single image evaluation

```python
from evalmedia import ImageEval
from evalmedia.checks.image import FaceArtifacts, PromptAdherence, TextLegibility

result = ImageEval.run(
    image="output.png",
    prompt="a woman holding a coffee cup in a cafe",
    checks=[FaceArtifacts(), PromptAdherence(), TextLegibility()],
)

print(result.passed)        # False
print(result.summary())     # "FAIL — 2/3 checks passed (score: 0.65). Failed: face_artifacts."
print(result.to_dict())     # structured JSON for agents
```

### Rubric-based evaluation

```python
from evalmedia import ImageEval
from evalmedia.rubrics import Portrait

result = ImageEval.run(
    image="output.png",
    prompt="professional headshot of a young man",
    rubric=Portrait(),
)
```

Built-in rubrics: `GeneralQuality`, `Portrait`, `MarketingAsset`.

### Async support

```python
result = await ImageEval.arun(
    image=image_bytes,
    prompt=prompt,
    checks=[FaceArtifacts(), PromptAdherence()],
)
```

### Compare multiple images

```python
from evalmedia import compare
from evalmedia.rubrics import GeneralQuality

results = await compare(
    images=["modelA.png", "modelB.png", "modelC.png"],
    prompt="a sunset over mountains",
    rubric=GeneralQuality(),
)

best_label, best_result = results.best()
```

## Checks

| Check | Type | What it evaluates |
|-------|------|-------------------|
| `PromptAdherence` | VLM | Does the image match what was asked for? |
| `FaceArtifacts` | VLM | Distorted faces, wrong eye count, melted features |
| `HandArtifacts` | VLM | Extra/missing fingers, distorted hands |
| `TextLegibility` | VLM | Is text in the image spelled correctly and readable? |
| `AestheticQuality` | VLM | Composition, lighting, color harmony |
| `StyleConsistency` | VLM | Does it match a style reference image? |
| `CLIPSimilarity` | Classical | CLIP cosine similarity between prompt and image |
| `ResolutionAdequacy` | Classical | Is the resolution sufficient? |

## Configuration

```python
import evalmedia

# Set global default judge
evalmedia.set_judge("claude", api_key="sk-...")

# Or via environment variables
# EVALMEDIA_DEFAULT_JUDGE=claude
# EVALMEDIA_ANTHROPIC_API_KEY=sk-...
# EVALMEDIA_OPENAI_API_KEY=sk-...
```

## CLI

```bash
# Evaluate an image
evalmedia check output.png --prompt "a woman in a cafe" --checks face_artifacts,prompt_adherence

# Use a rubric
evalmedia check output.png --prompt "headshot" --rubric portrait --format json

# Compare images
evalmedia compare outputs/ --prompt "sunset" --rubric general_quality

# List available checks and rubrics
evalmedia list-checks
evalmedia list-rubrics
```

## Agent Integration

Use evalmedia as a tool in AI agent workflows:

```python
from evalmedia.integrations import openai_tool_schema, anthropic_tool_schema

# OpenAI function calling
tools = [openai_tool_schema()]

# Anthropic tool_use
tools = [anthropic_tool_schema()]
```

## Custom Rubrics

```python
from evalmedia.rubrics import Rubric, WeightedCheck
from evalmedia.checks.image import PromptAdherence, TextLegibility, AestheticQuality

rubric = Rubric(
    name="my_rubric",
    checks=[
        WeightedCheck(check=PromptAdherence(), weight=0.4),
        WeightedCheck(check=TextLegibility(), weight=0.3),
        WeightedCheck(check=AestheticQuality(), weight=0.3),
    ],
    pass_threshold=0.75,
)
```

Or via YAML:

```yaml
name: my_rubric
pass_threshold: 0.75
checks:
  - check: prompt_adherence
    weight: 0.4
  - check: text_legibility
    weight: 0.3
  - check: aesthetic_quality
    weight: 0.3
```

## License

Apache 2.0
