from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values, load_dotenv
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
from chatbot_platform.infrastructure.tenants.tenant_config_loader import (
    list_tenant_ids,
    load_tenant_config,
)
from chatbot_platform.infrastructure.tenants.tenant_paths import resolve_tenant_paths
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_TENANTS_ROOT = _PROJECT_ROOT / "tenants"
_CHROMA_DIR = _PROJECT_ROOT / "chroma_db"
_PROMPTS_DIR = _PROJECT_ROOT / "prompts"
_DB_PATH = _PROJECT_ROOT / "conversations.sqlite3"
_STATIC_DIR = Path(__file__).parent / "static"
_DEFAULT_TENANT_ID = "default"


class TenantRuntime:
    def __init__(
        self,
        vector_store: VectorStore,
        llm_provider: LLMProvider,
        whatsapp_adapter: WhatsAppAdapter | None,
        instagram_adapter: InstagramAdapter | None,
        whatsapp_verify_token: str | None,
        instagram_verify_token: str | None,
    ) -> None:
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.whatsapp_adapter = whatsapp_adapter
        self.instagram_adapter = instagram_adapter
        self.whatsapp_verify_token = whatsapp_verify_token
        self.instagram_verify_token = instagram_verify_token


def _load_tenant_env(tenant_dir: Path) -> dict[str, str]:
    env_path = tenant_dir / ".env"
    if not env_path.exists():
        return {}
    return {key: value for key, value in dotenv_values(env_path).items() if value is not None}


def _create_whatsapp_adapter(tenant_env: dict[str, str]) -> WhatsAppAdapter | None:
    phone_number_id = tenant_env.get("WHATSAPP_PHONE_NUMBER_ID")
    access_token = tenant_env.get("WHATSAPP_ACCESS_TOKEN")
    if not phone_number_id or not access_token:
        return None
    return WhatsAppAdapter(phone_number_id=phone_number_id, access_token=access_token)


def _create_instagram_adapter(tenant_env: dict[str, str]) -> InstagramAdapter | None:
    ig_user_id = tenant_env.get("INSTAGRAM_IG_USER_ID")
    access_token = tenant_env.get("INSTAGRAM_ACCESS_TOKEN")
    if not ig_user_id or not access_token:
        return None
    return InstagramAdapter(ig_user_id=ig_user_id, access_token=access_token)


def _build_tenant_runtime(tenant_id: str) -> TenantRuntime:
    tenant_dir = _TENANTS_ROOT / tenant_id
    config = load_tenant_config(_TENANTS_ROOT, tenant_id)
    tenant_env = _load_tenant_env(tenant_dir)
    paths = resolve_tenant_paths(_TENANTS_ROOT, tenant_id)

    vector_store = ChromaVectorStore(
        persist_directory=_CHROMA_DIR, collection_name=paths.chroma_collection_name
    )
    index_knowledge_base(paths.knowledge_dir, vector_store)

    return TenantRuntime(
        vector_store=vector_store,
        llm_provider=create_llm_provider(config.llm_provider),
        whatsapp_adapter=_create_whatsapp_adapter(tenant_env),
        instagram_adapter=_create_instagram_adapter(tenant_env),
        whatsapp_verify_token=tenant_env.get("WHATSAPP_VERIFY_TOKEN"),
        instagram_verify_token=tenant_env.get("INSTAGRAM_VERIFY_TOKEN"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    load_dotenv(_PROJECT_ROOT / ".env")

    app.state.tenants = {
        tenant_id: _build_tenant_runtime(tenant_id) for tenant_id in list_tenant_ids(_TENANTS_ROOT)
    }
    app.state.conversation_repository = SqliteConversationRepository(_DB_PATH)

    yield


app = FastAPI(title="Chatbot Platform", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_tenant_runtime(tenant_id: str, request: Request) -> TenantRuntime:
    tenant = request.app.state.tenants.get(tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail=f"Bilinmeyen firma: {tenant_id}")
    return tenant


def get_conversation_repository(request: Request) -> ConversationRepository:
    return request.app.state.conversation_repository


def get_default_knowledge_dir() -> Path:
    return resolve_tenant_paths(_TENANTS_ROOT, _DEFAULT_TENANT_ID).knowledge_dir


def get_default_vector_store(request: Request) -> VectorStore:
    tenant = get_tenant_runtime(_DEFAULT_TENANT_ID, request)
    return tenant.vector_store


def _require_whatsapp_adapter(tenant: TenantRuntime = Depends(get_tenant_runtime)) -> ChannelAdapter:
    if tenant.whatsapp_adapter is None:
        raise HTTPException(status_code=503, detail="WhatsApp yapılandırılmamış")
    return tenant.whatsapp_adapter


def _require_instagram_adapter(tenant: TenantRuntime = Depends(get_tenant_runtime)) -> ChannelAdapter:
    if tenant.instagram_adapter is None:
        raise HTTPException(status_code=503, detail="Instagram yapılandırılmamış")
    return tenant.instagram_adapter


def _verify_webhook_challenge(
    hub_mode: str, hub_verify_token: str, hub_challenge: str, expected_token: str | None
) -> str:
    if hub_mode == "subscribe" and expected_token and hub_verify_token == expected_token:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Doğrulama başarısız")


@app.get("/t/{tenant_id}/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
    tenant: TenantRuntime = Depends(get_tenant_runtime),
) -> PlainTextResponse:
    challenge = _verify_webhook_challenge(
        hub_mode, hub_verify_token, hub_challenge, tenant.whatsapp_verify_token
    )
    return PlainTextResponse(challenge)


@app.post("/t/{tenant_id}/webhook/whatsapp")
async def receive_whatsapp_webhook(
    tenant_id: str,
    request: Request,
    whatsapp_adapter: ChannelAdapter = Depends(_require_whatsapp_adapter),
    tenant: TenantRuntime = Depends(get_tenant_runtime),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> dict[str, str]:
    payload = await request.json()
    handle_channel_message(
        payload,
        whatsapp_adapter,
        tenant.vector_store,
        tenant.llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
        tenant_id,
    )
    return {"status": "ok"}


@app.get("/t/{tenant_id}/webhook/instagram")
def verify_instagram_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
    tenant: TenantRuntime = Depends(get_tenant_runtime),
) -> PlainTextResponse:
    challenge = _verify_webhook_challenge(
        hub_mode, hub_verify_token, hub_challenge, tenant.instagram_verify_token
    )
    return PlainTextResponse(challenge)


@app.post("/t/{tenant_id}/webhook/instagram")
async def receive_instagram_webhook(
    tenant_id: str,
    request: Request,
    instagram_adapter: ChannelAdapter = Depends(_require_instagram_adapter),
    tenant: TenantRuntime = Depends(get_tenant_runtime),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> dict[str, str]:
    payload = await request.json()
    handle_channel_message(
        payload,
        instagram_adapter,
        tenant.vector_store,
        tenant.llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
        tenant_id,
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
def list_knowledge(
    knowledge_dir: Path = Depends(get_default_knowledge_dir),
) -> list[KnowledgeFileSummary]:
    return [KnowledgeFileSummary(**info) for info in list_knowledge_files(knowledge_dir)]


@app.get("/knowledge/{filename}", response_model=KnowledgeFileContent)
def get_knowledge_file(
    filename: str, knowledge_dir: Path = Depends(get_default_knowledge_dir)
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
    knowledge_dir: Path = Depends(get_default_knowledge_dir),
    vector_store: VectorStore = Depends(get_default_vector_store),
) -> None:
    try:
        save_knowledge_file(knowledge_dir, filename, save_request.content, vector_store)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz dosya adı") from exc


@app.delete("/knowledge/{filename}", status_code=204)
def delete_knowledge(
    filename: str,
    knowledge_dir: Path = Depends(get_default_knowledge_dir),
    vector_store: VectorStore = Depends(get_default_vector_store),
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


@app.post("/t/{tenant_id}/chat", response_model=ChatResponse)
def chat(
    tenant_id: str,
    chat_request: ChatRequest,
    tenant: TenantRuntime = Depends(get_tenant_runtime),
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
) -> ChatResponse:
    conversation_id = chat_request.conversation_id or f"{tenant_id}:{uuid4()}"
    answer = answer_question(
        chat_request.message,
        tenant.vector_store,
        tenant.llm_provider,
        _PROMPTS_DIR,
        conversation_repository,
        conversation_id,
    )
    return ChatResponse(answer=answer, conversation_id=conversation_id)
