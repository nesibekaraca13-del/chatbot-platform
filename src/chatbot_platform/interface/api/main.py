from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.application.use_cases.get_knowledge_file import get_knowledge_file_content
from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.application.use_cases.list_knowledge_files import list_knowledge_files
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
_STATIC_DIR = Path(__file__).parent / "static"


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
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_llm_provider(request: Request) -> LLMProvider:
    return request.app.state.llm_provider


def get_conversation_repository(request: Request) -> ConversationRepository:
    return request.app.state.conversation_repository


def get_knowledge_dir() -> Path:
    return _KNOWLEDGE_DIR


class KnowledgeFileSummary(BaseModel):
    filename: str
    category: str
    language: str
    last_updated: str
    heading_count: int


class KnowledgeFileContent(BaseModel):
    filename: str
    content: str


@app.get("/knowledge", response_model=list[KnowledgeFileSummary])
def list_knowledge(knowledge_dir: Path = Depends(get_knowledge_dir)) -> list[KnowledgeFileSummary]:
    return [KnowledgeFileSummary(**info) for info in list_knowledge_files(knowledge_dir)]


@app.get("/knowledge/{filename}", response_model=KnowledgeFileContent)
def get_knowledge_file(
    filename: str, knowledge_dir: Path = Depends(get_knowledge_dir)
) -> KnowledgeFileContent:
    try:
        content = get_knowledge_file_content(knowledge_dir, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz dosya adı") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı") from exc
    return KnowledgeFileContent(filename=filename, content=content)


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
