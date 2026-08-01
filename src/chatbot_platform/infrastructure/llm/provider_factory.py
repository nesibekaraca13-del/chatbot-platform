import os

from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.infrastructure.llm.claude_provider import create_claude_provider
from chatbot_platform.infrastructure.llm.gemini_provider import create_gemini_provider

_DEFAULT_PROVIDER = "claude"


def create_llm_provider(provider_override: str | None = None) -> LLMProvider:
    provider_name = (provider_override or os.environ.get("LLM_PROVIDER", _DEFAULT_PROVIDER)).lower()
    if provider_name == "claude":
        return create_claude_provider()
    if provider_name == "gemini":
        return create_gemini_provider()
    raise ValueError(f"Bilinmeyen LLM_PROVIDER: {provider_name}")
