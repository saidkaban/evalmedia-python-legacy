# Rubrics

A **rubric** is a named collection of weighted checks with a combined pass/fail threshold. Use rubrics when you want a single overall quality verdict for a specific use case.

## Built-in Rubrics

### GeneralQuality

Balanced default for most use cases.

```python
from evalmedia.rubrics import GeneralQuality

result = ImageEval.run(image="output.png", prompt="...", rubric=GeneralQuality())
```

| Check | Weight |
|-------|--------|
| PromptAdherence | 0.25 |
| AestheticQuality | 0.20 |
| FaceArtifacts | 0.15 |
| HandArtifacts | 0.15 |
| TextLegibility | 0.10 |
| ResolutionAdequacy | 0.10 |
| CLIPSimilarity | 0.05 |

Pass threshold: **0.65**

### Portrait

Optimized for face/headshot generation.

```python
from evalmedia.rubrics import Portrait

result = ImageEval.run(image="headshot.png", prompt="...", rubric=Portrait())
```

| Check | Weight |
|-------|--------|
| FaceArtifacts | 0.30 |
| PromptAdherence | 0.20 |
| AestheticQuality | 0.20 |
| HandArtifacts | 0.15 |
| ResolutionAdequacy | 0.15 |

Pass threshold: **0.70**

### MarketingAsset

Optimized for text-heavy marketing images.

```python
from evalmedia.rubrics import MarketingAsset

result = ImageEval.run(image="banner.png", prompt="...", rubric=MarketingAsset())
```

| Check | Weight |
|-------|--------|
| TextLegibility | 0.30 |
| PromptAdherence | 0.25 |
| AestheticQuality | 0.20 |
| ResolutionAdequacy | 0.15 |
| CLIPSimilarity | 0.10 |

Pass threshold: **0.70**

## Custom Rubrics

### Via Python

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

result = ImageEval.run(image="output.png", prompt="...", rubric=rubric)
```

### Via YAML

```yaml
# my_rubric.yaml
name: my_rubric
pass_threshold: 0.75
checks:
  - check: prompt_adherence
    weight: 0.4
  - check: text_legibility
    weight: 0.3
    threshold: 0.6
  - check: aesthetic_quality
    weight: 0.3
```

Load it:

```python
from evalmedia.rubrics import Rubric

rubric = Rubric.from_yaml("my_rubric.yaml")
```

Or use `load_rubric` which accepts both names and file paths:

```python
from evalmedia.rubrics import load_rubric

rubric = load_rubric("portrait")           # built-in name
rubric = load_rubric("my_rubric.yaml")     # YAML file path
```

## How Scoring Works

The rubric computes a weighted average of all check scores:

```
overall_score = Σ(weight_i × score_i) / Σ(weight_i)
passed = overall_score >= pass_threshold
```

Failed checks generate suggestions in `result.suggestions` — actionable text that agents can use to decide what to fix.
