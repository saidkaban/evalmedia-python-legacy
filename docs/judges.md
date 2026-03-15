# Judges

A **judge** is the VLM backend that powers VLM-based checks. evalmedia is backend-agnostic — choose based on your cost/quality/latency tradeoffs.

## Supported Judges

### Claude (Anthropic)

Recommended default for quality.

```bash
pip install evalmedia[claude]
```

```python
import evalmedia

evalmedia.set_judge("claude", api_key="sk-ant-...")

# Or via environment variable
# EVALMEDIA_ANTHROPIC_API_KEY=sk-ant-...
```

Default model: `claude-sonnet-4-20250514`. Override with:

```python
evalmedia.set_judge("claude", model="claude-opus-4-20250514")
```

### OpenAI (GPT-4.1)

Strong vision capabilities at reasonable cost.

```bash
pip install evalmedia[openai]
```

```python
import evalmedia

evalmedia.set_judge("openai", api_key="sk-...")

# Or via environment variable
# EVALMEDIA_OPENAI_API_KEY=sk-...
```

Default model: `gpt-4.1`. Override with:

```python
evalmedia.set_judge("openai", model="gpt-4.1-mini")
```

## Configuration Hierarchy

API keys and judge settings are resolved in this order (highest priority first):

1. **Function arguments** — `set_judge("claude", api_key="...")`
2. **Environment variables** — `EVALMEDIA_ANTHROPIC_API_KEY`
3. **Defaults** — Claude with no API key (will error on first call)

## Per-Check Judge Override

You can use different judges for different checks:

```python
from evalmedia.checks.image import FaceArtifacts, PromptAdherence

# Use Claude for face detection (higher quality)
face_check = FaceArtifacts(judge="claude")

# Use OpenAI for prompt adherence (lower cost)
prompt_check = PromptAdherence(judge="openai")
```

## How Judges Work

Each VLM check sends:

1. The image (as base64)
2. A check-specific evaluation prompt with scoring criteria
3. A system prompt requesting structured JSON output

The judge returns:

```json
{
  "reasoning": "Step-by-step analysis...",
  "score": 0.85,
  "passed": true,
  "confidence": 0.9
}
```

evalmedia parses this into a `JudgeResponse` with multiple fallback strategies (raw JSON, fenced code blocks, regex extraction).

## Retry Logic

Both judges include automatic retry with exponential backoff for transient errors (timeouts, connection errors). Configure via:

```bash
EVALMEDIA_MAX_RETRIES=3        # default: 3
EVALMEDIA_TIMEOUT_SECONDS=60   # default: 60
```
