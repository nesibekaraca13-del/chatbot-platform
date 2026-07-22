import os
from typing import Any

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.ports.llm_provider import LLMProvider

_DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiProvider(LLMProvider):
    def __init__(self, client: Any, model: str = _DEFAULT_MODEL) -> None:
        self._client = client
        self._model = model

    def generate(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                {"role": _to_gemini_role(m.role), "parts": [{"text": m.content}]}
                for m in messages
            ],
            config={"system_instruction": system_prompt},
        )
        return response.text


def _to_gemini_role(role: str) -> str:
    return "model" if role == "assistant" else "user"


def create_gemini_provider(model: str = _DEFAULT_MODEL) -> GeminiProvider:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return GeminiProvider(client=client, model=model)
