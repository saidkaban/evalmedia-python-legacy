"""Tests for VLM-powered checks using mock judge."""

import asyncio

from PIL import Image

from evalmedia.checks.image import (
    AestheticQuality,
    FaceArtifacts,
    HandArtifacts,
    PromptAdherence,
    StyleConsistency,
    TextLegibility,
)
from evalmedia.core import CheckStatus


class TestPromptAdherence:
    def test_pass(self, sample_image, mock_judge):
        check = PromptAdherence()
        result = asyncio.run(check.evaluate(sample_image, "a blue square", judge=mock_judge))
        assert result.passed is True
        assert result.score == 0.85
        assert result.name == "prompt_adherence"

    def test_fail(self, sample_image, mock_judge_fail):
        check = PromptAdherence()
        result = asyncio.run(check.evaluate(sample_image, "a red car", judge=mock_judge_fail))
        assert result.passed is False
        assert result.score == 0.25

    def test_prompt_template(self):
        check = PromptAdherence()
        prompt = check.get_check_prompt("a cat sitting on a table")
        assert "a cat sitting on a table" in prompt
        assert "Scoring guide" in prompt


class TestFaceArtifacts:
    def test_pass(self, sample_image, mock_judge):
        check = FaceArtifacts()
        result = asyncio.run(check.evaluate(sample_image, "portrait", judge=mock_judge))
        assert result.passed is True
        assert result.name == "face_artifacts"

    def test_prompt_template(self):
        check = FaceArtifacts()
        prompt = check.get_check_prompt("a woman smiling")
        assert "facial artifacts" in prompt.lower()
        assert "a woman smiling" in prompt


class TestHandArtifacts:
    def test_pass(self, sample_image, mock_judge):
        check = HandArtifacts()
        result = asyncio.run(check.evaluate(sample_image, "person waving", judge=mock_judge))
        assert result.passed is True
        assert result.name == "hand_artifacts"

    def test_prompt_template(self):
        check = HandArtifacts()
        prompt = check.get_check_prompt("person holding a cup")
        assert "finger" in prompt.lower()


class TestTextLegibility:
    def test_pass(self, sample_image, mock_judge):
        check = TextLegibility()
        result = asyncio.run(check.evaluate(sample_image, "sign with text", judge=mock_judge))
        assert result.passed is True
        assert result.name == "text_legibility"


class TestAestheticQuality:
    def test_pass(self, sample_image, mock_judge):
        check = AestheticQuality()
        result = asyncio.run(check.evaluate(sample_image, "beautiful sunset", judge=mock_judge))
        assert result.passed is True
        assert result.name == "aesthetic_quality"

    def test_prompt_template(self):
        check = AestheticQuality()
        prompt = check.get_check_prompt("landscape photo")
        assert "composition" in prompt.lower()
        assert "lighting" in prompt.lower()


class TestStyleConsistency:
    def test_skipped_no_reference(self, sample_image, mock_judge):
        check = StyleConsistency()
        result = asyncio.run(check.evaluate(sample_image, "test", judge=mock_judge))
        assert result.status == CheckStatus.SKIPPED
        assert "No reference" in result.reasoning

    def test_with_reference(self, sample_image, mock_judge):
        ref_image = Image.new("RGB", (256, 256), "red")
        check = StyleConsistency(reference=ref_image)
        result = asyncio.run(check.evaluate(sample_image, "test", judge=mock_judge))
        assert result.passed is True
        assert result.name == "style_consistency"
        # Judge should have received 2 images
        call_args = mock_judge.evaluate.call_args
        images = call_args.kwargs.get("image") or call_args[1].get("image")
        assert isinstance(images, list)
        assert len(images) == 2


class TestCustomThreshold:
    def test_high_threshold_fails(self, sample_image, mock_judge):
        # Mock returns 0.85, threshold 0.9 should fail
        check = PromptAdherence(threshold=0.9)
        result = asyncio.run(check.evaluate(sample_image, "test", judge=mock_judge))
        assert result.passed is False

    def test_low_threshold_passes(self, sample_image, mock_judge_fail):
        # Mock returns 0.25, threshold 0.2 should pass
        check = PromptAdherence(threshold=0.2)
        result = asyncio.run(check.evaluate(sample_image, "test", judge=mock_judge_fail))
        assert result.passed is True
