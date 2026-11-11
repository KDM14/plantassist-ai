import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.ingestion import ingest_documents, get_indexed_documents
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("/documents")
def list_documents():
    docs = get_indexed_documents()
    return {"documents": docs, "count": len(docs)}


@router.post("/documents/ingest")
def trigger_ingest(force: bool = False):
    try:
        stats = ingest_documents(force=force)
        return {
            "status": "completed",
            "processed": stats.get("processed", 0),
            "skipped": stats.get("skipped", 0),
            "failed": stats.get("failed", 0),
            "chunks_added": stats.get("chunks_added", 0),
            "documents": stats.get("documents", []),
        }
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400,
                            detail=f"Only PDF files are allowed. Got: {suffix}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit.")

    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Invalid PDF file (bad magic bytes).")

    docs_dir = Path(settings.DOCS_DIR)
    docs_dir.mkdir(parents=True, exist_ok=True)
    dest = docs_dir / file.filename

    with open(dest, "wb") as f:
        f.write(content)

    stats = ingest_documents(force=True)
    return {
        "status": "uploaded",
        "filename": file.filename,
        "size_bytes": len(content),
        "ingestion": stats,
    }
