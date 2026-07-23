from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.llm.provider_factory import create_llm_provider
from chatbot_platform.infrastructure.persistence.sqlite_conversation_repository import (
    SqliteConversationRepository,
)
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_KNOWLEDGE_DIR = _PROJECT_ROOT / "knowledge"
_CHROMA_DIR = _PROJECT_ROOT / "chroma_db"
_PROMPTS_DIR = _PROJECT_ROOT / "prompts"
_DB_PATH = _PROJECT_ROOT / "conversations.sqlite3"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    load_dotenv(_PROJECT_ROOT / ".env")

    vector_store = ChromaVectorStore(persist_directory=_CHROMA_DIR)
    index_knowledge_base(_KNOWLEDGE_DIR, vector_store)

    app.state.vector_store = vector_store
    app.state.llm_provider = create_llm_provider()
    app.state.conversation_repository = SqliteConversationRepository(_DB_PATH)

    yield


app = FastAPI(title="Chatbot Platform", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_llm_provider(request: Request) -> LLMProvider:
    return request.app.state.llm_provider


def get_conversation_repository(request: Request) -> ConversationRepository:
    return request.app.state.conversation_repository


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str


@app.post("/chat", response_model=ChatResponse)
def chat(
    chat_request: ChatRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> ChatResponse:
    conversation_id = chat_request.conversation_id or str(uuid4())
    answer = answer_question(
        chat_request.message,
        vector_store,
        llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
        conversation_id,
    )
    return ChatResponse(answer=answer, conversation_id=conversation_id)
