"""Shared test fixtures."""

from unittest.mock import AsyncMock

import pytest
from PIL import Image

from evalmedia.judges.base import JudgeResponse


@pytest.fixture
def sample_image() -> Image.Image:
    """512x512 blue test image."""
    return Image.new("RGB", (512, 512), color="blue")


@pytest.fixture
def large_image() -> Image.Image:
    """1920x1080 test image."""
    return Image.new("RGB", (1920, 1080), color="green")


@pytest.fixture
def small_image() -> Image.Image:
    """64x64 red test image."""
    return Image.new("RGB", (64, 64), color="red")


@pytest.fixture
def mock_judge():
    """Mock judge that returns a passing response."""
    judge = AsyncMock()
    judge.name = "mock"
    judge.evaluate.return_value = JudgeResponse(
        score=0.85,
        passed=True,
        confidence=0.9,
        reasoning="Mock evaluation: image looks good, no issues detected.",
        raw_output='{"score": 0.85, "passed": true, "confidence": 0.9, "reasoning": "Mock evaluation: image looks good, no issues detected."}',
        model="mock-model",
    )
    return judge


@pytest.fixture
def mock_judge_fail():
    """Mock judge that returns a failing response."""
    judge = AsyncMock()
    judge.name = "mock"
    judge.evaluate.return_value = JudgeResponse(
        score=0.25,
        passed=False,
        confidence=0.85,
        reasoning="Mock evaluation: significant artifacts detected in the image.",
        raw_output='{"score": 0.25, "passed": false, "confidence": 0.85, "reasoning": "Mock evaluation: significant artifacts detected in the image."}',
        model="mock-model",
    )
    return judge
