"""Tests for core data models."""

import pytest

from evalmedia.core import CheckResult, CheckStatus, CompareResult, EvalResult


class TestCheckResult:
    def test_create_passed(self):
        result = CheckResult(
            name="test_check",
            status=CheckStatus.PASSED,
            passed=True,
            score=0.9,
            confidence=0.95,
            reasoning="Looks good",
            threshold=0.5,
        )
        assert result.passed is True
        assert result.score == 0.9
        assert result.status == CheckStatus.PASSED

    def test_create_failed(self):
        result = CheckResult(
            name="test_check",
            status=CheckStatus.FAILED,
            passed=False,
            score=0.3,
        )
        assert result.passed is False
        assert result.status == CheckStatus.FAILED

    def test_create_error(self):
        result = CheckResult(
            name="test_check",
            status=CheckStatus.ERROR,
            error="Something went wrong",
        )
        assert result.status == CheckStatus.ERROR
        assert result.error == "Something went wrong"

    def test_create_skipped(self):
        result = CheckResult(
            name="style_consistency",
            status=CheckStatus.SKIPPED,
            reasoning="No reference image provided",
        )
        assert result.status == CheckStatus.SKIPPED

    def test_score_validation(self):
        with pytest.raises(ValueError):
            CheckResult(name="test", status=CheckStatus.PASSED, score=1.5)

        with pytest.raises(ValueError):
            CheckResult(name="test", status=CheckStatus.PASSED, score=-0.1)

    def test_confidence_validation(self):
        with pytest.raises(ValueError):
            CheckResult(name="test", status=CheckStatus.PASSED, confidence=2.0)

    def test_serialization(self):
        result = CheckResult(
            name="test",
            status=CheckStatus.PASSED,
            passed=True,
            score=0.8,
        )
        data = result.model_dump()
        assert data["name"] == "test"
        assert data["status"] == "passed"
        assert data["score"] == 0.8

    def test_defaults(self):
        result = CheckResult(name="test", status=CheckStatus.PASSED)
        assert result.passed is None
        assert result.score is None
        assert result.confidence is None
        assert result.reasoning == ""
        assert result.metadata == {}
        assert result.threshold == 0.5
        assert result.duration_ms == 0.0
        assert result.error is None


class TestEvalResult:
    def test_summary_pass(self):
        result = EvalResult(
            passed=True,
            overall_score=0.85,
            check_results=[
                CheckResult(name="check1", status=CheckStatus.PASSED, passed=True, score=0.9),
                CheckResult(name="check2", status=CheckStatus.PASSED, passed=True, score=0.8),
            ],
        )
        summary = result.summary()
        assert "PASS" in summary
        assert "2/2" in summary

    def test_summary_fail(self):
        result = EvalResult(
            passed=False,
            overall_score=0.45,
            check_results=[
                CheckResult(name="check1", status=CheckStatus.PASSED, passed=True, score=0.9),
                CheckResult(name="check2", status=CheckStatus.FAILED, passed=False, score=0.2),
            ],
        )
        summary = result.summary()
        assert "FAIL" in summary
        assert "1/2" in summary
        assert "check2" in summary

    def test_to_dict(self):
        result = EvalResult(
            passed=True,
            overall_score=0.8,
            check_results=[],
        )
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["passed"] is True
        assert data["overall_score"] == 0.8

    def test_score_validation(self):
        with pytest.raises(ValueError):
            EvalResult(passed=True, overall_score=1.5)


class TestCompareResult:
    def test_best(self):
        r1 = EvalResult(passed=True, overall_score=0.9)
        r2 = EvalResult(passed=False, overall_score=0.4)
        compare = CompareResult(
            rankings=[("image_a", r1), ("image_b", r2)],
            prompt="test",
        )
        label, result = compare.best()
        assert label == "image_a"
        assert result.overall_score == 0.9

    def test_best_empty(self):
        compare = CompareResult(rankings=[], prompt="test")
        with pytest.raises(ValueError):
            compare.best()
