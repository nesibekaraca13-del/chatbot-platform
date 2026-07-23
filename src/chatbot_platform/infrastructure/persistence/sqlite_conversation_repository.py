import sqlite3
from pathlib import Path

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


class SqliteConversationRepository(ConversationRepository):
    def __init__(self, db_path: Path) -> None:
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.execute(_CREATE_TABLE_SQL)
        self._connection.commit()

    def get_history(self, conversation_id: str, limit: int = 20) -> list[ChatMessage]:
        rows = self._connection.execute(
            "SELECT role, content FROM conversation_messages "
            "WHERE conversation_id = ? ORDER BY id DESC LIMIT ?",
            (conversation_id, limit),
        ).fetchall()
        rows.reverse()
        return [ChatMessage(role=role, content=content) for role, content in rows]

    def append_message(self, conversation_id: str, message: ChatMessage) -> None:
        self._connection.execute(
            "INSERT INTO conversation_messages (conversation_id, role, content) "
            "VALUES (?, ?, ?)",
            (conversation_id, message.role, message.content),
        )
        self._connection.commit()
