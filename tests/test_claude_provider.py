from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.infrastructure.llm.claude_provider import ClaudeProvider


class _FakeContentBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.content = [_FakeContentBlock(text)]


class _FakeMessages:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_call_kwargs: dict = {}

    def create(self, **kwargs: object) -> _FakeResponse:
        self.last_call_kwargs = kwargs
        return _FakeResponse(self._response_text)


class _FakeClient:
    def __init__(self, response_text: str) -> None:
        self.messages = _FakeMessages(response_text)


def test_generate_returns_response_text() -> None:
    fake_client = _FakeClient("Merhaba, size nasıl yardımcı olabilirim?")
    provider = ClaudeProvider(client=fake_client, model="claude-sonnet-5")

    result = provider.generate(
        system_prompt="Sen yardımcı bir asistansın.",
        messages=[ChatMessage(role="user", content="Merhaba")],
    )

    assert result == "Merhaba, size nasıl yardımcı olabilirim?"


def test_generate_passes_system_prompt_and_messages_to_client() -> None:
    fake_client = _FakeClient("ok")
    provider = ClaudeProvider(client=fake_client, model="claude-sonnet-5")

    provider.generate(
        system_prompt="SYSTEM",
        messages=[ChatMessage(role="user", content="Soru")],
    )

    call_kwargs = fake_client.messages.last_call_kwargs
    assert call_kwargs["system"] == "SYSTEM"
    assert call_kwargs["messages"] == [{"role": "user", "content": "Soru"}]
    assert call_kwargs["model"] == "claude-sonnet-5"
