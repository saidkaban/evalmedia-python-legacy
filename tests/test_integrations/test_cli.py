"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner

from evalmedia.cli.main import app

runner = CliRunner()


class TestCLI:
    def test_list_checks(self):
        result = runner.invoke(app, ["list-checks"])
        assert result.exit_code == 0
        assert "prompt_adherence" in result.output
        assert "face_artifacts" in result.output
        assert "resolution_adequacy" in result.output

    def test_list_rubrics(self):
        result = runner.invoke(app, ["list-rubrics"])
        assert result.exit_code == 0
        assert "general_quality" in result.output
        assert "portrait" in result.output
        assert "marketing_asset" in result.output

    def test_no_args_shows_help(self):
        result = runner.invoke(app, [])
        assert "evalmedia" in result.output.lower() or "usage" in result.output.lower()

    def test_check_missing_image(self):
        result = runner.invoke(app, ["check"])
        assert result.exit_code != 0
