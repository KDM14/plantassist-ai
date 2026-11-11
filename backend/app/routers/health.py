from fastapi import APIRouter
from app.schemas import HealthResponse
from app.config import settings
from app.database import get_ingested_documents

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    llm_configured = bool(
        settings.OPENAI_API_KEY
        or settings.GEMINI_API_KEY
        or settings.LLM_PROVIDER == "ollama"
    )

    try:
        from app.services.ingestion import get_chroma_collection
        collection = get_chroma_collection()
        chunk_count = collection.count()
        db_status = "healthy"
    except Exception as e:
        chunk_count = 0
        db_status = f"error: {str(e)}"

    doc_count = len(get_ingested_documents())

    return HealthResponse(
        status="healthy",
        llm_provider=settings.LLM_PROVIDER,
        llm_configured=llm_configured,
        vector_db_status=db_status,
        indexed_chunks=chunk_count,
        indexed_documents=doc_count,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION
    )
