# CLI

evalmedia includes a command-line interface for evaluating images from the terminal or CI/CD pipelines.

```bash
pip install evalmedia[cli]
```

## Commands

### `evalmedia check`

Evaluate a single image.

```bash
# With specific checks
evalmedia check output.png \
  --prompt "a woman in a cafe" \
  --checks face_artifacts,prompt_adherence

# With a rubric
evalmedia check output.png \
  --prompt "professional headshot" \
  --rubric portrait

# JSON output (for scripts/agents)
evalmedia check output.png \
  --prompt "headshot" \
  --rubric portrait \
  --format json

# One-line summary
evalmedia check output.png \
  --prompt "headshot" \
  --rubric portrait \
  --format summary
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `--prompt` | `-p` | Generation prompt |
| `--checks` | `-c` | Comma-separated check names |
| `--rubric` | `-r` | Rubric name or YAML path |
| `--judge` | `-j` | Judge backend (claude, openai) |
| `--format` | `-f` | Output format: table, json, summary |
| `--threshold` | `-t` | Override pass threshold |

**Exit codes:** `0` = passed, `1` = failed or error.

### `evalmedia compare`

Compare multiple images.

```bash
# Compare all images in a directory
evalmedia compare outputs/ \
  --prompt "a sunset over mountains" \
  --rubric general_quality

# Compare specific files
evalmedia compare "a.png,b.png,c.png" \
  --prompt "sunset" \
  --format json
```

### `evalmedia list-checks`

List all available checks.

```bash
evalmedia list-checks
```

### `evalmedia list-rubrics`

List all available rubrics with their checks and thresholds.

```bash
evalmedia list-rubrics
```

## CI/CD Usage

Use the exit code to gate deployments:

```yaml
# GitHub Actions example
- name: Evaluate generated image
  run: |
    evalmedia check output.png \
      --prompt "${{ env.PROMPT }}" \
      --rubric general_quality \
      --format summary
```

The command exits with code 1 if the image fails evaluation, which will fail the CI step.
