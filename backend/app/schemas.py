from pydantic import BaseModel, Field
from typing import List, Optional, Any


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000,
                          description="The question to ask the manufacturing copilot")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class SourceDocument(BaseModel):
    document_name: str
    page_number: int
    excerpt: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    evidence_status: str  # supported | insufficient | error | no_question
    abstained: bool
    conversation_id: str
    max_similarity: Optional[float] = None
    chunks_retrieved: Optional[int] = None
    chunks_relevant: Optional[int] = None


class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_hash: str
    page_count: Optional[int]
    chunk_count: Optional[int]
    ingested_at: str


class IngestResponse(BaseModel):
    status: str
    processed: int
    skipped: int
    failed: int
    chunks_added: int
    documents: List[Any]


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_configured: bool
    vector_db_status: str
    indexed_chunks: int
    indexed_documents: int
    app_name: str
    version: str
