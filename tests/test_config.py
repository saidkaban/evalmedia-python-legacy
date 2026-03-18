"""Tests for configuration."""

from evalmedia.config import EvalMediaConfig, get_config, set_judge


class TestConfig:
    def test_defaults(self):
        config = EvalMediaConfig()
        assert config.default_judge == "claude"
        assert config.timeout_seconds == 60.0
        assert config.max_retries == 3

    def test_env_var_override(self, monkeypatch):
        monkeypatch.setenv("EVALMEDIA_DEFAULT_JUDGE", "openai")
        monkeypatch.setenv("EVALMEDIA_TIMEOUT_SECONDS", "30.0")
        config = EvalMediaConfig()
        assert config.default_judge == "openai"
        assert config.timeout_seconds == 30.0

    def test_set_judge(self):
        import evalmedia.config as cfg

        # Reset singleton
        cfg._config = None

        set_judge("openai", api_key="test-key")
        config = get_config()
        assert config.default_judge == "openai"
        assert config.openai_api_key == "test-key"

        # Clean up
        cfg._config = None

    def test_set_judge_model(self):
        import evalmedia.config as cfg

        cfg._config = None
        set_judge("claude", model="claude-opus-4-20250514")
        config = get_config()
        assert config.default_model_claude == "claude-opus-4-20250514"

        cfg._config = None
