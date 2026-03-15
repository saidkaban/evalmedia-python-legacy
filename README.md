# evalmedia

Open-source framework for evaluating AI-generated media quality.

> **Status:** Under active development. V0.1.0 coming soon.

## Install

```bash
pip install evalmedia
```

## Quick Start

```python
from evalmedia import ImageEval
from evalmedia.checks.image import FaceArtifacts, PromptAdherence

result = ImageEval.run(
    image="output.png",
    prompt="a woman holding a coffee cup in a cafe",
    checks=[FaceArtifacts(), PromptAdherence()],
)

print(result.passed)
print(result.summary())
```

## License

Apache 2.0
