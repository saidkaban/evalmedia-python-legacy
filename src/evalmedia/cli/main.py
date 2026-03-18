"""CLI entry point for evalmedia."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="evalmedia",
    help="Evaluate AI-generated media quality.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def check(
    image: str = typer.Argument(..., help="Path or URL to the image"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Generation prompt"),
    checks: str | None = typer.Option(None, "--checks", "-c", help="Comma-separated check names"),
    rubric: str | None = typer.Option(None, "--rubric", "-r", help="Rubric name or YAML path"),
    judge: str | None = typer.Option(None, "--judge", "-j", help="Judge backend (claude, openai)"),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, summary"
    ),
    threshold: float | None = typer.Option(
        None, "--threshold", "-t", help="Override pass threshold"
    ),
    custom: list[str] | None = typer.Option(
        None, "--custom", help="Custom natural-language criterion (repeatable)"
    ),
) -> None:
    """Evaluate a single image."""
    from evalmedia.eval import ImageEval

    check_instances = None
    rubric_instance = None

    if rubric:
        from evalmedia.rubrics import load_rubric

        rubric_instance = load_rubric(rubric)
        if threshold is not None:
            rubric_instance.pass_threshold = threshold
    elif checks or custom:
        check_instances = []

        if checks:
            from evalmedia.checks import get_check

            check_names = [c.strip() for c in checks.split(",")]
            check_instances.extend(get_check(name) for name in check_names)

        if custom:
            from evalmedia.checks.custom import CustomCheck

            for i, criteria in enumerate(custom):
                name = f"custom_{i + 1}" if len(custom) > 1 else "custom"
                check_instances.append(
                    CustomCheck(
                        name=name,
                        criteria=criteria,
                        threshold=threshold,
                        judge=judge,
                    )
                )
    else:
        # Default to general quality rubric
        from evalmedia.rubrics import GeneralQuality

        rubric_instance = GeneralQuality()

    try:
        result = ImageEval.run(
            image=image,
            prompt=prompt,
            checks=check_instances,
            rubric=rubric_instance,
            judge=judge,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    _output_result(result, format)
    raise typer.Exit(0 if result.passed else 1)


@app.command()
def compare(
    images_dir: str = typer.Argument(..., help="Directory of images or comma-separated paths"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Generation prompt"),
    rubric: str | None = typer.Option("general_quality", "--rubric", "-r", help="Rubric name"),
    judge: str | None = typer.Option(None, "--judge", "-j", help="Judge backend"),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, summary"
    ),
) -> None:
    """Compare multiple images."""
    import asyncio

    from evalmedia.eval import compare as compare_fn
    from evalmedia.rubrics import load_rubric

    # Resolve images
    path = Path(images_dir)
    if path.is_dir():
        image_paths = sorted(
            str(p)
            for p in path.iterdir()
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp")
        )
        labels = [p.name for p in [Path(ip) for ip in image_paths]]
    else:
        image_paths = [p.strip() for p in images_dir.split(",")]
        labels = [Path(p).name for p in image_paths]

    if not image_paths:
        console.print("[red]No images found.[/red]")
        raise typer.Exit(1)

    rubric_instance = load_rubric(rubric) if rubric else None

    try:
        result = asyncio.run(
            compare_fn(
                images=image_paths,
                prompt=prompt,
                rubric=rubric_instance,
                judge=judge,
                labels=labels,
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if format == "json":
        console.print(json.dumps(result.model_dump(), indent=2, default=str))
    else:
        table = Table(title="Image Comparison Results")
        table.add_column("Rank", style="bold")
        table.add_column("Image")
        table.add_column("Score", justify="right")
        table.add_column("Passed")

        for i, (label, eval_result) in enumerate(result.rankings, 1):
            passed_str = "[green]PASS[/green]" if eval_result.passed else "[red]FAIL[/red]"
            table.add_row(str(i), label, f"{eval_result.overall_score:.2f}", passed_str)

        console.print(table)


@app.command(name="list-checks")
def list_checks_cmd() -> None:
    """List all available checks."""
    from evalmedia.checks.image import ALL_CHECKS

    table = Table(title="Available Checks")
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Description")

    for cls in ALL_CHECKS:
        table.add_row(cls.name, cls.check_type, cls.description)

    console.print(table)


@app.command(name="list-rubrics")
def list_rubrics_cmd() -> None:
    """List all available rubrics."""
    from evalmedia.rubrics import RUBRIC_REGISTRY

    table = Table(title="Available Rubrics")
    table.add_column("Name", style="bold")
    table.add_column("Checks")
    table.add_column("Threshold")

    for name, cls in RUBRIC_REGISTRY.items():
        instance = cls()
        check_names = ", ".join(wc.check.name for wc in instance.checks)
        table.add_row(name, check_names, str(instance.pass_threshold))

    console.print(table)


def _output_result(result, format: str) -> None:
    """Format and print an EvalResult."""
    if format == "json":
        console.print(json.dumps(result.to_dict(), indent=2, default=str))
    elif format == "summary":
        console.print(result.summary())
    else:
        # Table format
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        console.print(f"\nOverall: {status} (score: {result.overall_score:.2f})\n")

        table = Table()
        table.add_column("Check", style="bold")
        table.add_column("Status")
        table.add_column("Score", justify="right")
        table.add_column("Confidence", justify="right")
        table.add_column("Reasoning")

        for cr in result.check_results:
            if cr.status.value == "passed":
                status_str = "[green]PASS[/green]"
            elif cr.status.value == "failed":
                status_str = "[red]FAIL[/red]"
            elif cr.status.value == "error":
                status_str = "[yellow]ERROR[/yellow]"
            else:
                status_str = "[dim]SKIP[/dim]"

            score_str = f"{cr.score:.2f}" if cr.score is not None else "-"
            conf_str = f"{cr.confidence:.2f}" if cr.confidence is not None else "-"
            reasoning = (cr.reasoning[:80] + "...") if len(cr.reasoning) > 80 else cr.reasoning

            table.add_row(cr.name, status_str, score_str, conf_str, reasoning)

        console.print(table)

        if result.suggestions:
            console.print("\n[bold]Suggestions:[/bold]")
            for s in result.suggestions:
                console.print(f"  - {s}")


if __name__ == "__main__":
    app()
