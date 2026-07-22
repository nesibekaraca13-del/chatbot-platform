import os
from typing import Any

import anthropic

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.ports.llm_provider import LLMProvider

_DEFAULT_MODEL = "claude-sonnet-5"
_MAX_TOKENS = 1024


class ClaudeProvider(LLMProvider):
    def __init__(self, client: Any, model: str = _DEFAULT_MODEL) -> None:
        self._client = client
        self._model = model

    def generate(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return response.content[0].text


def create_claude_provider(model: str = _DEFAULT_MODEL) -> ClaudeProvider:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return ClaudeProvider(client=client, model=model)
