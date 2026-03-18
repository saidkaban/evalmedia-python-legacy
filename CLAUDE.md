# CLAUDE.md

## Workflow
- Make a separate git commit after each logical implementation phase.
- Use `uv` for Python environment and package management.
- Before every commit, run `uv run mypy src/evalmedia/` and `uv run ruff check src/ tests/` and fix any errors.
