"""Tests for tool schema exports."""

from evalmedia.integrations import anthropic_tool_schema, openai_tool_schema


class TestOpenAIToolSchema:
    def test_structure(self):
        schema = openai_tool_schema()
        assert schema["type"] == "function"
        assert "function" in schema
        func = schema["function"]
        assert func["name"] == "evaluate_image"
        assert "description" in func
        assert "parameters" in func

    def test_parameters(self):
        schema = openai_tool_schema()
        params = schema["function"]["parameters"]
        assert params["type"] == "object"
        assert "image_url" in params["properties"]
        assert "prompt" in params["properties"]
        assert "checks" in params["properties"]
        assert "rubric" in params["properties"]
        assert "image_url" in params["required"]

    def test_check_enum(self):
        schema = openai_tool_schema()
        checks_enum = schema["function"]["parameters"]["properties"]["checks"]["items"]["enum"]
        assert "prompt_adherence" in checks_enum
        assert "face_artifacts" in checks_enum
        assert "resolution_adequacy" in checks_enum

    def test_rubric_enum(self):
        schema = openai_tool_schema()
        rubric_enum = schema["function"]["parameters"]["properties"]["rubric"]["enum"]
        assert "general_quality" in rubric_enum
        assert "portrait" in rubric_enum
        assert "marketing_asset" in rubric_enum


class TestAnthropicToolSchema:
    def test_structure(self):
        schema = anthropic_tool_schema()
        assert schema["name"] == "evaluate_image"
        assert "description" in schema
        assert "input_schema" in schema

    def test_input_schema(self):
        schema = anthropic_tool_schema()
        input_schema = schema["input_schema"]
        assert input_schema["type"] == "object"
        assert "image_url" in input_schema["properties"]
        assert "image_url" in input_schema["required"]
