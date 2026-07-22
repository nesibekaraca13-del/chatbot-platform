from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.infrastructure.llm.gemini_provider import GeminiProvider


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeModels:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_call_kwargs: dict = {}

    def generate_content(self, **kwargs: object) -> _FakeResponse:
        self.last_call_kwargs = kwargs
        return _FakeResponse(self._response_text)


class _FakeClient:
    def __init__(self, response_text: str) -> None:
        self.models = _FakeModels(response_text)


def test_generate_returns_response_text() -> None:
    fake_client = _FakeClient("Merhaba, size nasıl yardımcı olabilirim?")
    provider = GeminiProvider(client=fake_client, model="gemini-2.5-flash")

    result = provider.generate(
        system_prompt="Sen yardımcı bir asistansın.",
        messages=[ChatMessage(role="user", content="Merhaba")],
    )

    assert result == "Merhaba, size nasıl yardımcı olabilirim?"


def test_generate_maps_assistant_role_to_model() -> None:
    fake_client = _FakeClient("ok")
    provider = GeminiProvider(client=fake_client, model="gemini-2.5-flash")

    provider.generate(
        system_prompt="SYSTEM",
        messages=[
            ChatMessage(role="user", content="Soru"),
            ChatMessage(role="assistant", content="Önceki cevap"),
        ],
    )

    call_kwargs = fake_client.models.last_call_kwargs
    assert call_kwargs["model"] == "gemini-2.5-flash"
    assert call_kwargs["config"] == {"system_instruction": "SYSTEM"}
    assert call_kwargs["contents"] == [
        {"role": "user", "parts": [{"text": "Soru"}]},
        {"role": "model", "parts": [{"text": "Önceki cevap"}]},
    ]
