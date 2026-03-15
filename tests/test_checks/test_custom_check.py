"""Tests for CustomCheck."""

import asyncio

import pytest
from PIL import Image

from evalmedia.checks import CustomCheck
from evalmedia.core import CheckStatus


class TestCustomCheckBasic:
    def test_returns_valid_check_result(self, sample_image, mock_judge):
        check = CustomCheck(name="brand", criteria="Is the image minimalist?")
        result = asyncio.run(
            check.evaluate(sample_image, "a clean design", judge=mock_judge)
        )
        assert result.passed is True
        assert result.score == 0.85
        assert result.name == "brand"
        assert result.status == CheckStatus.PASSED
        assert result.threshold == 0.5
        assert result.metadata["criteria"] == "Is the image minimalist?"
        assert result.metadata["invert"] is False

    def test_prompt_contains_criteria(self):
        check = CustomCheck(name="test", criteria="Does it have cool tones?")
        prompt = check.get_check_prompt("a sunset photo")
        assert "Does it have cool tones?" in prompt
        assert "a sunset photo" in prompt

    def test_custom_threshold(self, sample_image, mock_judge):
        check = CustomCheck(
            name="strict", criteria="Is this perfect?", threshold=0.9
        )
        result = asyncio.run(
            check.evaluate(sample_image, "test", judge=mock_judge)
        )
        # mock_judge returns 0.85, threshold 0.9 should fail
        assert result.passed is False
        assert result.status == CheckStatus.FAILED


class TestCustomCheckInvert:
    def test_invert_high_score_fails(self, sample_image, mock_judge):
        """High score + invert=True should FAIL (e.g., NSFW detection)."""
        check = CustomCheck(
            name="nsfw", criteria="Does this contain NSFW content?", invert=True
        )
        # mock_judge returns 0.85 >= 0.5 threshold, but inverted => FAIL
        result = asyncio.run(
            check.evaluate(sample_image, "test", judge=mock_judge)
        )
        assert result.passed is False
        assert result.status == CheckStatus.FAILED
        assert result.score == 0.85

    def test_invert_low_score_passes(self, sample_image, mock_judge_fail):
        """Low score + invert=True should PASS."""
        check = CustomCheck(
            name="nsfw", criteria="Does this contain NSFW content?", invert=True
        )
        # mock_judge_fail returns 0.25 < 0.5 threshold, inverted => PASS
        result = asyncio.run(
            check.evaluate(sample_image, "test", judge=mock_judge_fail)
        )
        assert result.passed is True
        assert result.status == CheckStatus.PASSED

    def test_invert_metadata(self, sample_image, mock_judge):
        check = CustomCheck(
            name="neg", criteria="Is it bad?", invert=True
        )
        result = asyncio.run(
            check.evaluate(sample_image, "test", judge=mock_judge)
        )
        assert result.metadata["invert"] is True


class TestCustomCheckValidation:
    def test_empty_criteria_raises(self):
        with pytest.raises(ValueError, match="criteria"):
            CustomCheck(name="test", criteria="")

    def test_whitespace_criteria_raises(self):
        with pytest.raises(ValueError, match="criteria"):
            CustomCheck(name="test", criteria="   ")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name"):
            CustomCheck(name="", criteria="Some criteria")

    def test_none_criteria_raises(self):
        with pytest.raises((ValueError, TypeError)):
            CustomCheck(name="test", criteria=None)


class TestCustomCheckIntegration:
    def test_works_with_image_eval(self, sample_image, mock_judge, mocker):
        from evalmedia.checks.image import PromptAdherence
        from evalmedia.eval import ImageEval

        mocker.patch("evalmedia.eval.get_judge", return_value=mock_judge)
        result = ImageEval.run(
            image=sample_image,
            prompt="a blue square",
            checks=[
                PromptAdherence(),
                CustomCheck(name="brand", criteria="Is the image on-brand?"),
            ],
        )
        assert len(result.check_results) == 2
        names = [r.name for r in result.check_results]
        assert "prompt_adherence" in names
        assert "brand" in names

    def test_works_in_rubric(self, sample_image, mock_judge, mocker):
        from evalmedia.checks.image import FaceArtifacts
        from evalmedia.eval import ImageEval
        from evalmedia.rubrics.base import Rubric, WeightedCheck

        mocker.patch("evalmedia.eval.get_judge", return_value=mock_judge)
        rubric = Rubric(
            name="custom_test",
            checks=[
                WeightedCheck(check=FaceArtifacts(), weight=0.5),
                WeightedCheck(
                    check=CustomCheck(name="brand", criteria="Is it on-brand?"),
                    weight=0.5,
                ),
            ],
            pass_threshold=0.7,
        )
        result = ImageEval.run(
            image=sample_image,
            prompt="a portrait",
            rubric=rubric,
        )
        assert len(result.check_results) == 2
        assert result.overall_score > 0
