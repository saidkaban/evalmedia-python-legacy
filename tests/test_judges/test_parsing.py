"""Tests for judge response parsing."""

import pytest

from evalmedia.judges._parsing import parse_judge_response


class TestParseJudgeResponse:
    def test_raw_json(self):
        raw = '{"reasoning": "Looks great", "score": 0.85, "passed": true, "confidence": 0.9}'
        resp = parse_judge_response(raw)
        assert resp.score == 0.85
        assert resp.passed is True
        assert resp.confidence == 0.9
        assert resp.reasoning == "Looks great"

    def test_fenced_json(self):
        raw = 'Here is my analysis:\n```json\n{"reasoning": "Good image", "score": 0.7, "passed": true, "confidence": 0.8}\n```'
        resp = parse_judge_response(raw)
        assert resp.score == 0.7
        assert resp.passed is True

    def test_fenced_no_language(self):
        raw = '```\n{"reasoning": "test", "score": 0.6, "passed": true, "confidence": 0.7}\n```'
        resp = parse_judge_response(raw)
        assert resp.score == 0.6

    def test_embedded_json(self):
        raw = 'My analysis shows this image is good. {"reasoning": "ok", "score": 0.9, "passed": true, "confidence": 0.95} That is my verdict.'
        resp = parse_judge_response(raw)
        assert resp.score == 0.9

    def test_regex_fallback(self):
        raw = 'The image quality is high. score: 0.75, passed: true, confidence: 0.8'
        resp = parse_judge_response(raw)
        assert resp.score == 0.75
        assert resp.passed is True
        assert resp.confidence == 0.8

    def test_score_clamping(self):
        raw = '{"reasoning": "test", "score": 1.5, "passed": true, "confidence": 0.9}'
        resp = parse_judge_response(raw)
        assert resp.score == 1.0

    def test_score_clamping_negative(self):
        raw = '{"reasoning": "test", "score": -0.5, "passed": false, "confidence": 0.9}'
        resp = parse_judge_response(raw)
        assert resp.score == 0.0

    def test_string_passed(self):
        raw = '{"reasoning": "test", "score": 0.8, "passed": "true", "confidence": 0.9}'
        resp = parse_judge_response(raw)
        assert resp.passed is True

    def test_model_and_usage(self):
        raw = '{"reasoning": "test", "score": 0.8, "passed": true, "confidence": 0.9}'
        resp = parse_judge_response(raw, model="claude-sonnet", usage={"input_tokens": 100})
        assert resp.model == "claude-sonnet"
        assert resp.usage["input_tokens"] == 100

    def test_extra_fields_in_metadata(self):
        raw = '{"reasoning": "test", "score": 0.8, "passed": true, "confidence": 0.9, "text_elements": ["Hello"]}'
        resp = parse_judge_response(raw)
        assert resp.metadata["text_elements"] == ["Hello"]

    def test_raw_output_preserved(self):
        raw = '{"reasoning": "test", "score": 0.5, "passed": true, "confidence": 0.7}'
        resp = parse_judge_response(raw)
        assert resp.raw_output == raw
