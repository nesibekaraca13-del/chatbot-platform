from pathlib import Path

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.infrastructure.persistence.sqlite_conversation_repository import (
    SqliteConversationRepository,
)


def test_append_and_get_history(tmp_path: Path) -> None:
    repo = SqliteConversationRepository(tmp_path / "test.db")

    repo.append_message("conv-1", ChatMessage(role="user", content="Merhaba"))
    repo.append_message(
        "conv-1",
        ChatMessage(role="assistant", content="Merhaba, size nasıl yardımcı olabilirim?"),
    )

    history = repo.get_history("conv-1")

    assert history == [
        ChatMessage(role="user", content="Merhaba"),
        ChatMessage(role="assistant", content="Merhaba, size nasıl yardımcı olabilirim?"),
    ]


def test_history_is_isolated_per_conversation(tmp_path: Path) -> None:
    repo = SqliteConversationRepository(tmp_path / "test.db")

    repo.append_message("conv-1", ChatMessage(role="user", content="A"))
    repo.append_message("conv-2", ChatMessage(role="user", content="B"))

    assert repo.get_history("conv-1") == [ChatMessage(role="user", content="A")]
    assert repo.get_history("conv-2") == [ChatMessage(role="user", content="B")]


def test_persists_across_repository_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    SqliteConversationRepository(db_path).append_message(
        "conv-1", ChatMessage(role="user", content="Merhaba")
    )

    reopened = SqliteConversationRepository(db_path)

    assert reopened.get_history("conv-1") == [ChatMessage(role="user", content="Merhaba")]


def test_get_history_respects_limit(tmp_path: Path) -> None:
    repo = SqliteConversationRepository(tmp_path / "test.db")
    for i in range(5):
        repo.append_message("conv-1", ChatMessage(role="user", content=f"mesaj {i}"))

    history = repo.get_history("conv-1", limit=2)

    assert history == [
        ChatMessage(role="user", content="mesaj 3"),
        ChatMessage(role="user", content="mesaj 4"),
    ]
