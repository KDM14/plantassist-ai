import logging
from typing import List, Dict

from app.config import settings

logger = logging.getLogger(__name__)

ABSTAIN_RESPONSE = (
    "I couldn't find sufficient information in the available manufacturing documents "
    "to answer this question reliably. Please consult your supervisor or the relevant "
    "equipment specialist."
)

SAFETY_WARNING = (
    "\n\n⚠️ **Safety Note**: For any safety-critical operations, always follow approved "
    "plant procedures and escalate uncertainty to your responsible supervisor before proceeding."
)

SYSTEM_PROMPT = """You are PlantAssist AI, an expert manufacturing knowledge assistant for Kaveri Precision Components, Hosur Plant.
You answer questions EXCLUSIVELY based on the provided document excerpts.

STRICT RULES:
1. Answer ONLY using the provided context. Never use general knowledge to fill gaps.
2. If the context does not contain a clear answer, say explicitly: "The available documents do not contain this information."
3. Never fabricate specifications, tolerances, maintenance schedules, safety procedures, or machine parameters.
4. Always cite which document and page number your answer comes from.
5. For safety-related questions, remind the user to follow approved plant procedures.
6. Be concise and direct — supervisors need quick, actionable answers on the shop floor.
7. If you see contradictory information between documents, note it and advise checking the latest revision.
8. Do not use Markdown formatting beyond **bold** for emphasis. Keep responses readable on mobile screens.

You are NOT allowed to guess, infer beyond what is explicitly written, or use training knowledge to fill missing information."""


def build_rag_prompt(question: str, context_chunks: List[Dict]) -> List[Dict]:
    """Build the messages list for LLM API call."""
    if not context_chunks:
        context_text = "No relevant document excerpts found."
    else:
        parts = []
        for i, chunk in enumerate(context_chunks, 1):
            parts.append(
                f"[Source {i}: {chunk['document_name']}, Page {chunk['page_number']}]\n{chunk['text']}"
            )
        context_text = "\n\n---\n\n".join(parts)

    user_message = (
        f"DOCUMENT CONTEXT:\n{context_text}\n\n"
        f"---\n\n"
        f"QUESTION: {question}\n\n"
        f"Based ONLY on the document excerpts above, provide a clear and accurate answer. "
        f"If the answer is not in the documents, say so explicitly. "
        f"Always state which document and page number your answer comes from."
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]


def call_openai_compatible(messages: List[Dict], model: str, base_url: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def call_gemini(messages: List[Dict], model: str, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(
        model,
        system_instruction=next((m["content"] for m in messages if m["role"] == "system"), "")
    )
    user_text = next((m["content"] for m in messages if m["role"] == "user"), "")
    response = gemini_model.generate_content(user_text)
    return response.text


def call_ollama(messages: List[Dict], model: str, base_url: str) -> str:
    import httpx
    response = httpx.post(
        f"{base_url}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=120.0
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def is_safety_question(question: str) -> bool:
    """Detect if a question is safety-related."""
    safety_keywords = [
        "lockout", "tagout", "loto", "safety", "hazard", "emergency",
        "accident", "injury", "electric", "electrical", "energized",
        "dangerous", "risk", "protect", "guard", "isolate", "isolation",
        "lock", "tag", "zero energy"
    ]
    q_lower = question.lower()
    return any(kw in q_lower for kw in safety_keywords)


def generate_answer_fallback(question: str, context_chunks: List[Dict],
                              is_safety_related: bool = False) -> str:
    """
    Fallback answer when no LLM is configured.
    Returns the most relevant document excerpts clearly labeled, with no fabrication.
    """
    if not context_chunks:
        return ABSTAIN_RESPONSE

    best = context_chunks[0]
    source_line = f"[Source: {best['document_name']}, Page {best['page_number']}]"

    parts = []
    for chunk in context_chunks[:3]:
        src = f"{chunk['document_name']}, Page {chunk['page_number']}"
        parts.append(f"From {src}:\n{chunk['text']}")

    answer = (
        f"Based on the manufacturing documents, here is the most relevant information:\n\n"
        + "\n\n---\n\n".join(parts)
        + "\n\n"
        + "ℹ️ Note: Answers are displayed directly from document excerpts. "
        + "Configure an LLM API key (OPENAI_API_KEY or GEMINI_API_KEY) for synthesised, conversational answers."
    )

    if is_safety_related:
        answer += SAFETY_WARNING

    return answer


def generate_answer(question: str, context_chunks: List[Dict],
                    is_safety_related: bool = False) -> str:
    """Generate answer using configured LLM provider, with fallback to direct excerpts."""
    messages = build_rag_prompt(question, context_chunks)
    provider = settings.LLM_PROVIDER.lower()

    # Check if any LLM is reachable
    has_llm = bool(
        (provider == "gemini" and settings.GEMINI_API_KEY)
        or (provider == "ollama")
        or settings.OPENAI_API_KEY
    )

    if not has_llm:
        logger.info("No LLM configured — using direct excerpt fallback mode.")
        return generate_answer_fallback(question, context_chunks, is_safety_related)

    try:
        if provider == "gemini" and settings.GEMINI_API_KEY:
            answer = call_gemini(messages, settings.GEMINI_MODEL, settings.GEMINI_API_KEY)
        elif provider == "ollama":
            try:
                answer = call_ollama(messages, settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)
            except Exception as ollama_err:
                logger.warning(f"Ollama unavailable: {ollama_err}. Using fallback.")
                return generate_answer_fallback(question, context_chunks, is_safety_related)
        elif settings.OPENAI_API_KEY:
            answer = call_openai_compatible(
                messages, settings.OPENAI_MODEL,
                settings.OPENAI_BASE_URL, settings.OPENAI_API_KEY
            )
        else:
            return generate_answer_fallback(question, context_chunks, is_safety_related)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise

    if is_safety_related:
        answer += SAFETY_WARNING

    return answer
