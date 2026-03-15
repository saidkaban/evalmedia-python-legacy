"""Tests for ResolutionAdequacy check (no API needed)."""

import asyncio

import pytest
from PIL import Image

from evalmedia.checks.image import ResolutionAdequacy
from evalmedia.core import CheckStatus


class TestResolutionAdequacy:
    def test_pass_large_image(self, sample_image):
        check = ResolutionAdequacy(min_width=256, min_height=256)
        result = asyncio.run(check.arun(sample_image))
        assert result.passed is True
        assert result.status == CheckStatus.PASSED
        assert result.score == 1.0
        assert result.confidence == 1.0

    def test_fail_small_image(self, small_image):
        check = ResolutionAdequacy(min_width=512, min_height=512)
        result = asyncio.run(check.arun(small_image))
        assert result.passed is False
        assert result.status == CheckStatus.FAILED
        assert result.score < 1.0

    def test_exact_match(self):
        img = Image.new("RGB", (512, 512))
        check = ResolutionAdequacy(min_width=512, min_height=512)
        result = asyncio.run(check.arun(img))
        assert result.passed is True
        assert result.score == 1.0

    def test_preset_target_web(self):
        check = ResolutionAdequacy(target="web")
        assert check.min_width == 1024
        assert check.min_height == 1024

    def test_preset_target_hd(self):
        check = ResolutionAdequacy(target="hd")
        assert check.min_width == 1920
        assert check.min_height == 1080

    def test_metadata(self, sample_image):
        check = ResolutionAdequacy(min_width=256, min_height=256)
        result = asyncio.run(check.arun(sample_image))
        assert result.metadata["width"] == 512
        assert result.metadata["height"] == 512
        assert result.metadata["min_width"] == 256
        assert result.metadata["min_height"] == 256

    def test_custom_threshold(self, small_image):
        check = ResolutionAdequacy(min_width=128, min_height=128, threshold=0.9)
        result = asyncio.run(check.arun(small_image))
        assert result.threshold == 0.9

    def test_partial_score(self):
        # Image meets width but not height
        img = Image.new("RGB", (1024, 256))
        check = ResolutionAdequacy(min_width=512, min_height=512)
        result = asyncio.run(check.arun(img))
        assert result.passed is False
        assert 0.0 < result.score < 1.0
