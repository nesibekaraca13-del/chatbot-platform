from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore

_SYSTEM_PROMPT_TEMPLATE = """Sen bir firmanın müşteri hizmetleri asistanısın. \
Sadece aşağıda verilen Bilgi Kaynağı'nı kullanarak cevap ver. Bilgi Kaynağı'nda \
cevap yoksa "Bu konuda elimde bilgi yok, sizi bir yetkiliye yönlendiriyorum." de. \
Bilgi Kaynağı dışına çıkıp tahmin yürütme.

Bilgi Kaynağı:
{context}
"""


def answer_question(
    question: str,
    vector_store: VectorStore,
    llm_provider: LLMProvider,
    top_k: int = 3,
) -> str:
    relevant_chunks = vector_store.search(question, top_k=top_k)
    context = "\n\n".join(chunk.text for chunk in relevant_chunks)
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(context=context)
    return llm_provider.generate(
        system_prompt=system_prompt,
        messages=[ChatMessage(role="user", content=question)],
    )
