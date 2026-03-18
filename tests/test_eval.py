"""Tests for ImageEval runner."""

import asyncio
from unittest.mock import patch

import pytest

from evalmedia.checks.image import PromptAdherence, ResolutionAdequacy
from evalmedia.core import CheckStatus, EvalResult
from evalmedia.eval import ImageEval


class TestImageEval:
    def test_arun_with_checks(self, sample_image, mock_judge):
        async def run():
            with patch("evalmedia.eval.get_judge", return_value=mock_judge):
                return await ImageEval.arun(
                    image=sample_image,
                    prompt="a blue square",
                    checks=[ResolutionAdequacy(min_width=256, min_height=256)],
                )

        result = asyncio.run(run())
        assert isinstance(result, EvalResult)
        assert result.passed is True
        assert len(result.check_results) == 1
        assert result.duration_ms > 0

    def test_arun_mixed_checks(self, sample_image, mock_judge):
        async def run():
            with patch("evalmedia.eval.get_judge", return_value=mock_judge):
                return await ImageEval.arun(
                    image=sample_image,
                    prompt="a blue square",
                    checks=[
                        ResolutionAdequacy(min_width=256, min_height=256),
                        PromptAdherence(),
                    ],
                )

        result = asyncio.run(run())
        assert len(result.check_results) == 2
        assert result.passed is True

    def test_arun_no_checks_or_rubric(self, sample_image):
        with pytest.raises(ValueError, match="Either 'checks' or 'rubric'"):
            asyncio.run(ImageEval.arun(image=sample_image, prompt="test"))

    def test_arun_with_rubric(self, sample_image, mock_judge):
        from evalmedia.rubrics import Portrait

        async def run():
            with patch("evalmedia.eval.get_judge", return_value=mock_judge):
                return await ImageEval.arun(
                    image=sample_image,
                    prompt="professional headshot",
                    rubric=Portrait(),
                )

        result = asyncio.run(run())
        assert isinstance(result, EvalResult)
        assert len(result.check_results) == 5  # Portrait has 5 checks

    def test_check_error_handling(self, sample_image, mock_judge):
        """A check that throws should not crash the whole evaluation."""
        mock_judge.evaluate.side_effect = RuntimeError("API error")

        async def run():
            with patch("evalmedia.eval.get_judge", return_value=mock_judge):
                return await ImageEval.arun(
                    image=sample_image,
                    prompt="test",
                    checks=[PromptAdherence()],
                )

        result = asyncio.run(run())
        assert len(result.check_results) == 1
        assert result.check_results[0].status == CheckStatus.ERROR
        assert "API error" in result.check_results[0].error

    def test_concurrent_execution(self, sample_image, mock_judge):
        """Multiple checks should run concurrently."""

        async def run():
            with patch("evalmedia.eval.get_judge", return_value=mock_judge):
                return await ImageEval.arun(
                    image=sample_image,
                    prompt="test",
                    checks=[
                        ResolutionAdequacy(min_width=256, min_height=256),
                        ResolutionAdequacy(min_width=1024, min_height=1024),
                        ResolutionAdequacy(min_width=128, min_height=128),
                    ],
                )

        result = asyncio.run(run())
        assert len(result.check_results) == 3
