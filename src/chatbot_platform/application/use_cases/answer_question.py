from pathlib import Path

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.prompts.prompt_renderer import render_system_prompt


def answer_question(
    question: str,
    vector_store: VectorStore,
    llm_provider: LLMProvider,
    prompts_dir: Path,
    top_k: int = 3,
) -> str:
    relevant_chunks = vector_store.search(question, top_k=top_k)
    context = "\n\n".join(chunk.text for chunk in relevant_chunks)
    system_prompt = render_system_prompt(prompts_dir, context=context)
    return llm_provider.generate(
        system_prompt=system_prompt,
        messages=[ChatMessage(role="user", content=question)],
    )
