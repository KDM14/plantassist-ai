import logging
import uuid
from typing import Optional, Dict, Any

from app.services.retrieval import retrieve_relevant_chunks, evaluate_evidence, format_sources
from app.services.llm import generate_answer, ABSTAIN_RESPONSE, is_safety_question
from app.database import save_message
from app.config import settings

logger = logging.getLogger(__name__)


def process_question(question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Main RAG pipeline: retrieve → evaluate → generate → respond."""
    if not question or not question.strip():
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "evidence_status": "no_question",
            "abstained": True,
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "max_similarity": 0.0,
            "chunks_retrieved": 0,
            "chunks_relevant": 0,
        }

    conv_id = conversation_id or str(uuid.uuid4())
    question = question.strip()

    # Save user message
    save_message(conv_id, "user", question)

    # Step 1: Retrieve
    chunks = retrieve_relevant_chunks(question, top_k=settings.TOP_K_RESULTS)
    logger.info(f"Retrieved {len(chunks)} chunks for query: '{question[:60]}'")

    # Step 2: Evaluate evidence (threshold + lexical overlap guard)
    has_evidence, relevant_chunks, max_similarity = evaluate_evidence(chunks, query=question)
    logger.info(
        f"Evidence: has={has_evidence}, max_sim={max_similarity:.3f}, relevant={len(relevant_chunks)}"
    )

    # Step 3: Safety context
    safety_related = is_safety_question(question)

    # Step 4: Generate or abstain
    if not has_evidence:
        answer = ABSTAIN_RESPONSE
        # Still show nearest sources for transparency (but mark as abstained)
        sources = format_sources(chunks[:2]) if chunks else []
        evidence_status = "insufficient"
        abstained = True
    else:
        try:
            answer = generate_answer(question, relevant_chunks, is_safety_related=safety_related)
            sources = format_sources(relevant_chunks)
            evidence_status = "supported"
            abstained = False
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            answer = (
                f"I found relevant information in the documents but encountered an error "
                f"generating the answer. Please check the LLM configuration."
            )
            sources = format_sources(relevant_chunks)
            evidence_status = "error"
            abstained = False

    # Save assistant response
    save_message(conv_id, "assistant", answer,
                 sources=sources, evidence_status=evidence_status, abstained=abstained)

    return {
        "answer": answer,
        "sources": sources,
        "evidence_status": evidence_status,
        "abstained": abstained,
        "conversation_id": conv_id,
        "max_similarity": max_similarity,
        "chunks_retrieved": len(chunks),
        "chunks_relevant": len(relevant_chunks),
    }
