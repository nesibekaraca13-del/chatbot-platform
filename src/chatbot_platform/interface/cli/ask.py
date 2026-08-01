import sys
from pathlib import Path

from dotenv import load_dotenv

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.infrastructure.llm.provider_factory import create_llm_provider
from chatbot_platform.infrastructure.persistence.sqlite_conversation_repository import (
    SqliteConversationRepository,
)
from chatbot_platform.infrastructure.tenants.tenant_paths import resolve_tenant_paths
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_TENANTS_ROOT = _PROJECT_ROOT / "tenants"
_TENANT_ID = "default"
_TENANT_PATHS = resolve_tenant_paths(_TENANTS_ROOT, _TENANT_ID)
_CHROMA_DIR = _PROJECT_ROOT / "chroma_db"
_PROMPTS_DIR = _PROJECT_ROOT / "prompts"
_DB_PATH = _PROJECT_ROOT / "conversations.sqlite3"
_CLI_CONVERSATION_ID = f"{_TENANT_ID}:cli-demo"


def main() -> None:
    load_dotenv(_PROJECT_ROOT / ".env")

    question = " ".join(sys.argv[1:])
    if not question:
        print("Kullanım: python -m chatbot_platform.interface.cli.ask <soru>")
        return

    vector_store = ChromaVectorStore(
        persist_directory=_CHROMA_DIR, collection_name=_TENANT_PATHS.chroma_collection_name
    )
    index_knowledge_base(_TENANT_PATHS.knowledge_dir, vector_store)

    llm_provider = create_llm_provider()
    conversation_repository = SqliteConversationRepository(_DB_PATH)

    print(
        answer_question(
            question,
            vector_store,
            llm_provider,
            _PROMPTS_DIR,
            conversation_repository,
            _CLI_CONVERSATION_ID,
        )
    )


if __name__ == "__main__":
    main()
