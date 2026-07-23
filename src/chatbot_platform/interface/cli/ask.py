import sys
from pathlib import Path

from dotenv import load_dotenv

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.infrastructure.llm.provider_factory import create_llm_provider
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_KNOWLEDGE_DIR = _PROJECT_ROOT / "knowledge"
_CHROMA_DIR = _PROJECT_ROOT / "chroma_db"
_PROMPTS_DIR = _PROJECT_ROOT / "prompts"


def main() -> None:
    load_dotenv(_PROJECT_ROOT / ".env")

    question = " ".join(sys.argv[1:])
    if not question:
        print("Kullanım: python -m chatbot_platform.interface.cli.ask <soru>")
        return

    vector_store = ChromaVectorStore(persist_directory=_CHROMA_DIR)
    index_knowledge_base(_KNOWLEDGE_DIR, vector_store)

    llm_provider = create_llm_provider()
    print(answer_question(question, vector_store, llm_provider, _PROMPTS_DIR))


if __name__ == "__main__":
    main()
