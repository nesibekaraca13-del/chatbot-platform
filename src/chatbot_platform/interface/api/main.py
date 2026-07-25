import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.application.use_cases.delete_knowledge_file import delete_knowledge_file
from chatbot_platform.application.use_cases.get_knowledge_file import get_knowledge_file_content
from chatbot_platform.application.use_cases.handle_channel_message import handle_channel_message
from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.application.use_cases.list_knowledge_files import list_knowledge_files
from chatbot_platform.application.use_cases.save_knowledge_file import save_knowledge_file
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.channels.instagram_adapter import InstagramAdapter
from chatbot_platform.infrastructure.channels.whatsapp_adapter import WhatsAppAdapter
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
    app.state.whatsapp_adapter = _create_whatsapp_adapter_if_configured()
    app.state.instagram_adapter = _create_instagram_adapter_if_configured()

    yield


def _create_whatsapp_adapter_if_configured() -> WhatsAppAdapter | None:
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    if not phone_number_id or not access_token:
        return None
    return WhatsAppAdapter(phone_number_id=phone_number_id, access_token=access_token)


def _create_instagram_adapter_if_configured() -> InstagramAdapter | None:
    ig_user_id = os.environ.get("INSTAGRAM_IG_USER_ID")
    access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    if not ig_user_id or not access_token:
        return None
    return InstagramAdapter(ig_user_id=ig_user_id, access_token=access_token)


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


def get_whatsapp_adapter(request: Request) -> ChannelAdapter:
    adapter = request.app.state.whatsapp_adapter
    if adapter is None:
        raise HTTPException(status_code=503, detail="WhatsApp yapılandırılmamış")
    return adapter


def get_instagram_adapter(request: Request) -> ChannelAdapter:
    adapter = request.app.state.instagram_adapter
    if adapter is None:
        raise HTTPException(status_code=503, detail="Instagram yapılandırılmamış")
    return adapter


def _verify_webhook_challenge(hub_mode: str, hub_verify_token: str, hub_challenge: str, env_var: str) -> str:
    expected_token = os.environ.get(env_var, "")
    if hub_mode == "subscribe" and expected_token and hub_verify_token == expected_token:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Doğrulama başarısız")


@app.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse:
    challenge = _verify_webhook_challenge(
        hub_mode, hub_verify_token, hub_challenge, "WHATSAPP_VERIFY_TOKEN"
    )
    return PlainTextResponse(challenge)


@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    whatsapp_adapter: ChannelAdapter = Depends(get_whatsapp_adapter),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> dict[str, str]:
    payload = await request.json()
    handle_channel_message(
        payload,
        whatsapp_adapter,
        vector_store,
        llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
    )
    return {"status": "ok"}


@app.get("/webhook/instagram")
def verify_instagram_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse:
    challenge = _verify_webhook_challenge(
        hub_mode, hub_verify_token, hub_challenge, "INSTAGRAM_VERIFY_TOKEN"
    )
    return PlainTextResponse(challenge)


@app.post("/webhook/instagram")
async def receive_instagram_webhook(
    request: Request,
    instagram_adapter: ChannelAdapter = Depends(get_instagram_adapter),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> dict[str, str]:
    payload = await request.json()
    handle_channel_message(
        payload,
        instagram_adapter,
        vector_store,
        llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
    )
    return {"status": "ok"}


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


class SaveKnowledgeFileRequest(BaseModel):
    content: str


@app.put("/knowledge/{filename}", status_code=204)
def save_knowledge(
    filename: str,
    save_request: SaveKnowledgeFileRequest,
    knowledge_dir: Path = Depends(get_knowledge_dir),
    vector_store: VectorStore = Depends(get_vector_store),
) -> None:
    try:
        save_knowledge_file(knowledge_dir, filename, save_request.content, vector_store)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz dosya adı") from exc


@app.delete("/knowledge/{filename}", status_code=204)
def delete_knowledge(
    filename: str,
    knowledge_dir: Path = Depends(get_knowledge_dir),
    vector_store: VectorStore = Depends(get_vector_store),
) -> None:
    try:
        delete_knowledge_file(knowledge_dir, filename, vector_store)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz dosya adı") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı") from exc


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
