# evalmedia

**Open-source framework for evaluating AI-generated media quality.**

Think "DeepEval but for generative media." Structured, actionable quality assessments for AI-generated images — designed for AI agents, not dashboards.

---

## Why evalmedia?

When an AI agent generates an image, it needs to answer: *Is this good enough to ship?* Not a vague score — specific, decomposed checks:

- Does this face have artifacts?
- Does this match the prompt?
- Is the text in this image legible?

evalmedia gives agents structured answers they can act on — retry, adjust, or switch models.

## Key Features

- **8 built-in checks** — face artifacts, hand artifacts, prompt adherence, text legibility, aesthetic quality, style consistency, CLIP similarity, resolution adequacy
- **VLM-powered** — uses Claude or GPT-4.1 as judges for subjective quality assessment
- **Classical checks** — CLIP similarity and resolution checks with no API needed
- **Rubrics** — weighted check collections for specific use cases (portraits, marketing assets)
- **Agent-native** — tool schemas for OpenAI and Anthropic function calling
- **Async-first** — concurrent check execution via `asyncio.gather`
- **CLI included** — evaluate images from the command line

## Quick Example

```python
from evalmedia import ImageEval
from evalmedia.checks.image import FaceArtifacts, PromptAdherence

result = ImageEval.run(
    image="output.png",
    prompt="a woman holding a coffee cup in a cafe",
    checks=[FaceArtifacts(), PromptAdherence()],
)

print(result.passed)     # True/False
print(result.summary())  # "PASS — 2/2 checks passed (score: 0.85)."
print(result.to_dict())  # structured JSON for agents
```

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
