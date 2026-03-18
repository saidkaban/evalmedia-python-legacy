"""Tests for rubric system."""

from pathlib import Path

import pytest

from evalmedia.core import CheckResult, CheckStatus
from evalmedia.rubrics import (
    GeneralQuality,
    MarketingAsset,
    Portrait,
    Rubric,
    WeightedCheck,
    load_rubric,
)


class TestWeightedScoring:
    def test_compute_result_pass(self):
        from evalmedia.checks.image import PromptAdherence, ResolutionAdequacy

        rubric = Rubric(
            name="test",
            checks=[
                WeightedCheck(check=PromptAdherence(), weight=0.6),
                WeightedCheck(check=ResolutionAdequacy(), weight=0.4),
            ],
            pass_threshold=0.7,
        )

        results = [
            CheckResult(name="prompt_adherence", status=CheckStatus.PASSED, score=0.9),
            CheckResult(name="resolution_adequacy", status=CheckStatus.PASSED, score=0.8),
        ]

        eval_result = rubric.compute_result(results)
        expected = (0.6 * 0.9 + 0.4 * 0.8) / 1.0
        assert abs(eval_result.overall_score - expected) < 0.01
        assert eval_result.passed is True

    def test_compute_result_fail(self):
        from evalmedia.checks.image import PromptAdherence, ResolutionAdequacy

        rubric = Rubric(
            name="test",
            checks=[
                WeightedCheck(check=PromptAdherence(), weight=0.5),
                WeightedCheck(check=ResolutionAdequacy(), weight=0.5),
            ],
            pass_threshold=0.7,
        )

        results = [
            CheckResult(name="prompt_adherence", status=CheckStatus.FAILED, score=0.3),
            CheckResult(name="resolution_adequacy", status=CheckStatus.PASSED, score=0.8),
        ]

        eval_result = rubric.compute_result(results)
        expected = (0.5 * 0.3 + 0.5 * 0.8) / 1.0
        assert abs(eval_result.overall_score - expected) < 0.01
        assert eval_result.passed is False

    def test_suggestions_from_failed(self):
        from evalmedia.checks.image import FaceArtifacts, PromptAdherence

        rubric = Rubric(
            name="test",
            checks=[
                WeightedCheck(check=PromptAdherence(), weight=0.5),
                WeightedCheck(check=FaceArtifacts(), weight=0.5),
            ],
            pass_threshold=0.7,
        )

        results = [
            CheckResult(
                name="prompt_adherence",
                status=CheckStatus.PASSED,
                score=0.9,
                reasoning="Good match",
            ),
            CheckResult(
                name="face_artifacts",
                status=CheckStatus.FAILED,
                score=0.2,
                reasoning="Extra finger detected",
            ),
        ]

        eval_result = rubric.compute_result(results)
        assert len(eval_result.suggestions) == 1
        assert "Extra finger" in eval_result.suggestions[0]


class TestBuiltinRubrics:
    def test_general_quality(self):
        r = GeneralQuality()
        assert r.name == "general_quality"
        assert len(r.checks) == 7
        total = sum(wc.weight for wc in r.checks)
        assert abs(total - 1.0) < 0.01

    def test_portrait(self):
        r = Portrait()
        assert r.name == "portrait"
        assert len(r.checks) == 5
        total = sum(wc.weight for wc in r.checks)
        assert abs(total - 1.0) < 0.01

    def test_marketing_asset(self):
        r = MarketingAsset()
        assert r.name == "marketing_asset"
        assert len(r.checks) == 5
        total = sum(wc.weight for wc in r.checks)
        assert abs(total - 1.0) < 0.01


class TestLoadRubric:
    def test_load_by_name(self):
        r = load_rubric("portrait")
        assert r.name == "portrait"

    def test_load_general_quality(self):
        r = load_rubric("general_quality")
        assert r.name == "general_quality"

    def test_load_invalid(self):
        with pytest.raises(ValueError, match="not found"):
            load_rubric("nonexistent_rubric")

    def test_load_yaml_template(self):
        template_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "evalmedia"
            / "rubrics"
            / "templates"
            / "portrait.yaml"
        )
        if template_path.exists():
            r = Rubric.from_yaml(template_path)
            assert r.name == "portrait"
            assert len(r.checks) > 0
