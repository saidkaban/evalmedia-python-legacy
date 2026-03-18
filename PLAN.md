# evalmedia — Open-Source Media Output Quality Evaluation Framework for Agents

**Website:** evalmedia.com
**PyPI:** `pip install evalmedia`
**Import:** `import evalmedia`

## What This Is

evalmedia is an open-source Python framework for evaluating the quality of AI-generated media (images, video, audio). Think "DeepEval but for generative media." It gives developers and AI agents structured, actionable quality assessments of generated outputs — not a single score, but decomposed checks that answer specific questions like "does this face have artifacts?", "does this match the prompt?", "is the text in this image legible?"

The key differentiator: this is designed to be **agent-native**. The primary consumer of evaluation results is not a human looking at a dashboard — it's an AI agent in a creative workflow that needs to decide whether to ship, retry, adjust, or switch models.

## Core Concepts

### 1. Checks

The fundamental unit. A Check answers a specific, bounded question about a media output. Each check returns a structured `CheckResult`:

```python
@dataclass
class CheckResult:
    name: str              # e.g. "face_artifacts"
    passed: bool           # binary verdict
    score: float           # 0.0 to 1.0 graded score
    confidence: float      # judge's confidence in this assessment
    reasoning: str         # human-readable explanation
    metadata: dict         # check-specific extra data (e.g. detected regions, counts)
    threshold: float       # the threshold used for pass/fail
```

Checks fall into two categories:

- **Classical checks**: Use traditional CV/ML metrics. No LLM/VLM needed. Examples: CLIP similarity, LPIPS, SSIM, FID, face detection confidence, text OCR extraction. These are fast, cheap, deterministic.
- **VLM-powered checks**: Use a vision-language model as a judge to answer a structured question about the image. Examples: "Does this face look natural?", "Is this consistent with the style reference?", "Does this image match the prompt intent?" These are slower, cost money, but can assess subjective/complex qualities.

### 2. Judges

A Judge is the backend that powers VLM-powered checks. evalmedia is backend-agnostic — users choose which VLM to use based on their cost/quality/latency tradeoff.

Ship with adapters for:
- **Claude** (via Anthropic API) — recommended default for quality
- **GPT-4.1** (via OpenAI API) — strong vision capabilities at reasonable cost
- **Gemini** (via Google AI API)
- **Open-source VLMs** (via local inference or API — InternVL2, Qwen2.5-VL)

The Judge interface:

```python
class Judge(Protocol):
    async def evaluate(self, image: Image, prompt: str, check_prompt: str) -> JudgeResponse:
        """Send an image + evaluation prompt to the VLM and get a structured response."""
        ...
```

Each judge adapter handles the specifics of formatting the request, parsing the response, and extracting the structured score. The check itself doesn't know or care which judge is running it.

Configuration:

```python
import evalmedia

# Global default
evalmedia.set_judge("claude", api_key="...")

# Per-check override
result = checks.FaceArtifacts(judge="gpt-4.1").run(image)

# Local/free judge
result = checks.FaceArtifacts(judge="internvl2-local").run(image)
```

### 3. Rubrics

A Rubric is a named collection of checks with weights and a combined pass/fail threshold. It represents a specific quality standard for a specific use case.

```python
# Built-in rubric
rubric = rubrics.Portrait()  # pre-configured for portrait/headshot generation

# Custom rubric via code
rubric = Rubric(
    name="marketing_asset",
    checks=[
        WeightedCheck(checks.PromptAdherence(), weight=0.3),
        WeightedCheck(checks.TextLegibility(), weight=0.3),
        WeightedCheck(checks.AestheticQuality(), weight=0.2),
        WeightedCheck(checks.ResolutionAdequacy(), weight=0.1),
        WeightedCheck(checks.BrandColorMatch(palette=["#FF5733", "#1A1A2E"]), weight=0.1),
    ],
    pass_threshold=0.75,
)

# Custom rubric via YAML (for non-Python agents/configs)
# rubrics/marketing_asset.yaml
# name: marketing_asset
# pass_threshold: 0.75
# checks:
#   - check: prompt_adherence
#     weight: 0.3
#   - check: text_legibility
#     weight: 0.3
#   ...
```

### 4. EvalResult (top-level response)

When a user runs an evaluation (either with individual checks or a rubric), they get back an `EvalResult`:

```python
@dataclass
class EvalResult:
    passed: bool                    # overall pass/fail
    overall_score: float            # weighted combined score
    check_results: list[CheckResult]  # individual check breakdowns
    suggestions: list[str]          # actionable retry suggestions for agents
    duration_ms: float              # total evaluation time
    judge_used: str                 # which judge backend was used
    
    def to_dict(self) -> dict:
        """Agent-friendly JSON serialization."""
        ...
    
    def summary(self) -> str:
        """Human-readable summary string."""
        ...
```

The `suggestions` field is key for agent usage. Instead of just "FAIL", the result says things like:
- "Face artifact detected on left hand (extra finger). Retry with inpainting or negative prompt 'extra fingers'."
- "Prompt adherence low — image is missing the 'red hat' element. Consider emphasizing this in the prompt."

## Developer Experience

### Quick start — single image eval

```python
from evalmedia import ImageEval
from evalmedia.checks.image import FaceArtifacts, PromptAdherence, TextLegibility

result = ImageEval.run(
    image="output.png",  # accepts path, URL, PIL.Image, bytes, base64
    prompt="a woman holding a coffee cup in a cafe",
    checks=[FaceArtifacts(), PromptAdherence(), TextLegibility()],
)

print(result.passed)        # False
print(result.summary())     # "FAIL — 2/3 checks passed. FaceArtifacts: FAIL (extra finger detected)"
print(result.to_dict())     # structured JSON for agents
```

### Rubric-based eval

```python
from evalmedia import ImageEval
from evalmedia.rubrics import Portrait

result = ImageEval.run(
    image="output.png",
    prompt="professional headshot of a young man",
    rubric=Portrait(),
)
```

### Batch eval (comparing model outputs)

```python
from evalmedia import compare

results = compare(
    images=["modelA_output.png", "modelB_output.png", "modelC_output.png"],
    prompt="a sunset over mountains",
    rubric=rubrics.GeneralQuality(),
)

# Returns ranked results with per-model breakdowns
best = results.best()  # the image that scored highest
```

### Async support (critical for agent workflows)

```python
result = await ImageEval.arun(
    image=image_bytes,
    prompt=prompt,
    checks=[FaceArtifacts(), PromptAdherence()],
)
```

### CLI (for CI/CD pipelines and scripts)

```bash
# Evaluate a single image
evalmedia check output.png --prompt "a woman in a cafe" --checks face_artifacts,prompt_adherence

# Evaluate with a rubric
evalmedia check output.png --prompt "..." --rubric portrait

# Batch compare
evalmedia compare outputs/ --prompt "..." --rubric general_quality --format json
```

## Agent Integrations

### OpenAI-compatible function/tool schema

Ship a JSON schema that can be used directly in OpenAI/Anthropic tool_use:

```python
from evalmedia.integrations import openai_tool_schema, anthropic_tool_schema

tools = [openai_tool_schema()]  # ready to pass to OpenAI's tools parameter
```

### LangChain / LangGraph Tool

```python
from evalmedia.integrations.langchain import EvalMediaTool

tool = EvalMediaTool()
# Use directly in a LangChain agent
```

## Project Structure

```
evalmedia/
├── pyproject.toml
├── README.md
├── PLAN.md                          # this document
├── LICENSE                          # Apache 2.0
│
├── src/
│   └── evalmedia/
│       ├── __init__.py              # top-level exports: ImageEval, VideoEval, AudioEval
│       ├── core.py                  # EvalResult, CheckResult, base classes
│       ├── eval.py                  # ImageEval, VideoEval, AudioEval runner classes
│       ├── config.py                # global config, judge defaults, API keys
│       │
│       ├── checks/
│       │   ├── __init__.py          # check registry, discovery
│       │   ├── base.py              # BaseCheck abstract class
│       │   ├── image/
│       │   │   ├── __init__.py
│       │   │   ├── face_artifacts.py
│       │   │   ├── prompt_adherence.py
│       │   │   ├── text_legibility.py
│       │   │   ├── aesthetic_quality.py
│       │   │   ├── style_consistency.py
│       │   │   ├── resolution_adequacy.py
│       │   │   ├── hand_artifacts.py
│       │   │   ├── clip_similarity.py       # classical check (prompt ↔ image)
│       │   │   ├── image_similarity.py     # classical check (image ↔ image, CLIP/DINOv2)
│       │   │   └── lpips_similarity.py      # classical check
│       │   ├── video/                       # v2 — not in initial release
│       │   │   └── ...
│       │   └── audio/                       # v2 — not in initial release
│       │       └── ...
│       │
│       ├── judges/
│       │   ├── __init__.py          # judge registry
│       │   ├── base.py              # Judge protocol/ABC
│       │   ├── claude.py            # Anthropic Messages API
│       │   ├── openai.py            # OpenAI Responses API + structured output
│       │   ├── openrouter.py        # OpenRouter gateway (OpenAI-compatible)
│       │   ├── gemini.py
│       │   └── local.py             # adapter for local VLMs via transformers/vllm
│       │
│       ├── rubrics/
│       │   ├── __init__.py          # rubric registry, YAML loader
│       │   ├── base.py              # Rubric, WeightedCheck classes
│       │   ├── portrait.py
│       │   ├── marketing_asset.py
│       │   ├── general_quality.py
│       │   └── templates/           # YAML rubric templates
│       │       ├── portrait.yaml
│       │       ├── marketing_asset.yaml
│       │       └── general_quality.yaml
│       │
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── openai_tools.py      # OpenAI function/tool schema export
│       │   ├── anthropic_tools.py   # Anthropic tool schema export
│       │   └── langchain.py         # LangChain Tool wrapper
│       │
│       └── cli/
│           ├── __init__.py
│           └── main.py              # CLI entry point (click or typer)
│
├── tests/
│   ├── conftest.py
│   ├── test_checks/
│   │   ├── test_face_artifacts.py
│   │   ├── test_prompt_adherence.py
│   │   └── ...
│   ├── test_judges/
│   ├── test_rubrics/
│   └── test_integrations/
│
├── benchmarks/                      # calibration data + human agreement measurement
│   ├── README.md
│   ├── datasets/                    # small curated test sets with human labels
│   │   └── face_artifacts_v1/
│   │       ├── metadata.json        # image paths, prompts, human labels
│   │       └── images/
│   └── scripts/
│       └── measure_agreement.py     # script to run checks vs human labels and compute agreement
│
├── examples/
│   ├── quickstart.py
│   ├── agent_workflow.py            # example: agent generates → evals → retries
│   ├── model_comparison.py          # example: compare 3 models on same prompt set
│   └── custom_check.py             # example: how to write your own check
│
└── docs/
    ├── getting_started.md
    ├── architecture.md
    ├── writing_checks.md
    ├── writing_rubrics.md
    └── agent_integration.md
```

## V1 Scope — What to Build First

The first release should be tight, opinionated, and immediately useful. Image-only. 6-8 checks. One or two judge backends working well. Clean DX.

### V1 Checks (Image only)

| Check | Type | What it evaluates |
|-------|------|-------------------|
| `PromptAdherence` | VLM | Does the image match what was asked for? |
| `FaceArtifacts` | VLM + classical | Distorted faces, wrong eye count, melted features |
| `HandArtifacts` | VLM | Extra/missing fingers, distorted hands |
| `TextLegibility` | VLM + OCR | If text is present, is it spelled correctly and readable? |
| `AestheticQuality` | VLM | General visual appeal, composition, lighting |
| `StyleConsistency` | VLM | Does this match a provided style reference image? (requires ref) |
| `CLIPSimilarity` | Classical | CLIP cosine similarity between prompt and image |
| `ImageSimilarity` | Classical | Embedding-based image-to-image cosine similarity (CLIP/DINOv2) |
| `ResolutionAdequacy` | Classical | Is the resolution sufficient for the intended use? |
| `CustomCheck` | VLM (user-defined) | User-defined evaluation criteria in natural language |

### V1 Judge Backends

- Claude (Anthropic API) — primary, best quality
- GPT-4.1 (OpenAI Responses API) — structured output via strict JSON schema
- OpenRouter — gateway to 200+ models (Gemini, Llama, Mistral, etc.) via OpenAI-compatible API
- Others can be community-contributed after launch

### V1 Rubrics

- `GeneralQuality` — balanced default rubric for most use cases
- `Portrait` — optimized for face/headshot generation
- `MarketingAsset` — optimized for text-heavy marketing images

### V1 Integrations

- CLI
- OpenAI/Anthropic tool schemas (so agents can call evalmedia as a function)

### V1 NOT in scope

- Video evaluation (v2)
- Audio evaluation (v2)
- LangChain/LangGraph integration (v2 — keep the interface ready but don't ship adapter yet)
- Local VLM judge adapters (v2 — focus on cloud API judges first)
- Web dashboard or UI (not in v1 — may come later as a managed cloud offering)
- Benchmark datasets with human agreement scores (v2 — build the infrastructure for it in v1 but don't block launch on having calibration data)

### Future Improvements

- **Standalone custom check YAML files**: Allow defining custom checks as standalone YAML files (not only inside rubrics), so they can be referenced by name with `--checks` on the CLI. Currently custom criteria checks can only be defined inline in a rubric YAML or via `--custom` on the CLI.

## Implementation Priorities (Build Order)

### Phase 1: Core abstractions + one working check

Get the data model right first. Build `CheckResult`, `EvalResult`, `BaseCheck`, `Judge` protocol, and the `ImageEval` runner. Implement one end-to-end check (`PromptAdherence`) with the Claude judge to prove the full loop works.

Deliverable: `ImageEval.run(image, prompt, checks=[PromptAdherence()])` returns a correct, structured result.

### Phase 2: All V1 checks + second judge

Implement remaining 7 checks. Add GPT-4.1 judge. Make sure all checks work with both judges. Add the rubric system + 3 built-in rubrics.

Deliverable: Full rubric-based evaluation works end-to-end.

### Phase 3: Agent integrations + CLI

Build the tool schema exports and CLI. This is what makes it "for agents" instead of just another eval library.

Deliverable: An agent using OpenAI or Anthropic tool_use can call evalmedia checks as functions.

### Phase 4: Async, batch, compare

Add async support (`arun`), batch evaluation, and the `compare()` function for model comparison workflows.

Deliverable: Production-ready performance for real workloads.

### Phase 5: Polish + open-source launch

README, docs, examples, contributor guide. Package on PyPI. Benchmark infrastructure (even if datasets are small/initial).

Deliverable: Public GitHub repo that people can pip install and start using.

## Key Technical Decisions

### VLM Judge Prompting Strategy

Each VLM-powered check sends a carefully crafted prompt to the judge. The prompt should:
1. Describe exactly what to look for (specific, not vague)
2. Ask for a structured response (score, pass/fail, reasoning)
3. Include calibration examples where helpful ("a score of 0.3 means visible artifacts that a casual viewer would notice")
4. Request the reasoning BEFORE the score (chain-of-thought improves accuracy)

The prompt template for each check is the check's most important asset — this is where the quality lives. Store these as structured prompt templates, not inline strings.

### Image Input Handling

Accept all common formats and normalize internally:
- File path (str or Path)
- URL (http/https — download and cache)
- PIL.Image object
- Raw bytes
- Base64 string

Normalize everything to PIL.Image internally, then convert to the format each judge needs (base64 for API judges, tensor for local judges).

### Error Handling

- Judge API failures should not crash the evaluation. A failed check returns a `CheckResult` with `passed=None`, `score=None`, and an error in metadata.
- Timeout handling per check and per evaluation.
- Retry logic with exponential backoff for transient API errors.
- Clear error messages when API keys are missing or invalid.

### Configuration Hierarchy

1. Function arguments (highest priority)
2. Environment variables (`EVALMEDIA_JUDGE`, `EVALMEDIA_ANTHROPIC_API_KEY`, etc.)
3. Config file (`evalmedia.yaml` or `pyproject.toml [tool.evalmedia]` section)
4. Sensible defaults (lowest priority)

### Dependencies — Keep Them Minimal

Core package should have minimal required dependencies:
- `Pillow` — image handling
- `httpx` — async HTTP for judge APIs
- `pydantic` — data models

Optional dependency groups:
- `evalmedia[claude]` — adds `anthropic` SDK
- `evalmedia[openai]` — adds `openai` SDK
- `evalmedia[classical]` — adds `torch`, `transformers`, `clip` for classical checks
- `evalmedia[all]` — everything

## Package Identity

- **PyPI package:** `evalmedia`
- **Import:** `import evalmedia`
- **GitHub repo:** `evalmedia`
- **Domain:** `evalmedia.com`
- **CLI command:** `evalmedia`

## License

Apache 2.0 — permissive, allows commercial use, standard for open-source dev tools.
