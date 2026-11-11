import logging
from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import process_question
from app.database import get_conversation_history

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = process_question(request.question, request.conversation_id)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            evidence_status=result["evidence_status"],
            abstained=result["abstained"],
            conversation_id=result["conversation_id"],
            max_similarity=result.get("max_similarity"),
            chunks_retrieved=result.get("chunks_retrieved"),
            chunks_relevant=result.get("chunks_relevant"),
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}")
def get_history(conversation_id: str):
    history = get_conversation_history(conversation_id)
    return {"conversation_id": conversation_id, "messages": history}
