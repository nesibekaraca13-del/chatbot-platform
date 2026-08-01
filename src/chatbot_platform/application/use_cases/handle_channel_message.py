from pathlib import Path

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore


def handle_channel_message(
    payload: dict,
    channel_adapter: ChannelAdapter,
    vector_store: VectorStore,
    llm_provider: LLMProvider,
    prompts_dir: Path,
    conversation_repository: ConversationRepository,
    tenant_id: str,
) -> bool:
    incoming = channel_adapter.parse_incoming(payload)
    if incoming is None:
        return False

    conversation_id = f"{tenant_id}:{incoming.channel}:{incoming.external_user_id}"
    answer = answer_question(
        incoming.text,
        vector_store,
        llm_provider,
        prompts_dir,
        conversation_repository,
        conversation_id,
    )
    channel_adapter.send_message(incoming.external_user_id, answer)
    return True
