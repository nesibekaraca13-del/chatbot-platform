import pytest

from chatbot_platform.infrastructure.llm import provider_factory


def test_defaults_to_claude_when_env_var_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr(provider_factory, "create_claude_provider", lambda: "claude-instance")
    monkeypatch.setattr(provider_factory, "create_gemini_provider", lambda: "gemini-instance")

    assert provider_factory.create_llm_provider() == "claude-instance"


def test_selects_gemini_when_env_var_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setattr(provider_factory, "create_claude_provider", lambda: "claude-instance")
    monkeypatch.setattr(provider_factory, "create_gemini_provider", lambda: "gemini-instance")

    assert provider_factory.create_llm_provider() == "gemini-instance"


def test_raises_on_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "unknown")

    with pytest.raises(ValueError):
        provider_factory.create_llm_provider()
