import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.pdf_extractor import extract_pdf, chunk_text, compute_file_hash
from app.database import save_ingested_document, get_document_hash, get_ingested_documents

logger = logging.getLogger(__name__)

_embedding_model = None
_chroma_client = None
_collection = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model


def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def ingest_documents(docs_dir: str = None, force: bool = False) -> Dict[str, Any]:
    docs_dir = docs_dir or settings.DOCS_DIR
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        return {"error": f"Documents directory not found: {docs_dir}",
                "processed": 0, "skipped": 0, "failed": 0, "chunks_added": 0, "documents": []}

    pdf_files = list(docs_path.glob("*.pdf"))
    if not pdf_files:
        return {"error": "No PDF files found",
                "processed": 0, "skipped": 0, "failed": 0, "chunks_added": 0, "documents": []}

    # Exclude sample questions document from ingestion
    pdf_files = [
        f for f in pdf_files
        if "sample_questions" not in f.name.lower() and "sample questions" not in f.name.lower()
    ]

    model = get_embedding_model()
    collection = get_chroma_collection()

    stats: Dict[str, Any] = {
        "processed": 0, "skipped": 0, "failed": 0,
        "chunks_added": 0, "documents": []
    }

    for pdf_path in sorted(pdf_files):
        filename = pdf_path.name

        # Check if already ingested and unchanged
        if not force:
            current_hash = compute_file_hash(str(pdf_path))
            stored_hash = get_document_hash(filename)
            if stored_hash and stored_hash == current_hash:
                logger.info(f"Skipping unchanged document: {filename}")
                stats["skipped"] += 1
                continue

        logger.info(f"Processing: {filename}")
        doc_content = extract_pdf(str(pdf_path))

        if doc_content.error:
            logger.error(f"Failed to extract {filename}: {doc_content.error}")
            stats["failed"] += 1
            stats["documents"].append({"filename": filename, "status": "failed",
                                       "error": doc_content.error})
            continue

        if doc_content.is_scanned:
            logger.warning(
                f"Document {filename} appears to be scanned (low text). OCR may be needed."
            )

        # Build chunks from all pages
        all_chunks: List[dict] = []
        for page in doc_content.pages:
            if not page.text.strip():
                continue
            page_chunks = chunk_text(
                page.text, page.page_number, filename,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP
            )
            all_chunks.extend(page_chunks)

        if not all_chunks:
            logger.warning(f"No text chunks extracted from {filename}")
            stats["failed"] += 1
            stats["documents"].append({"filename": filename, "status": "failed",
                                       "error": "No extractable text"})
            continue

        # Remove existing entries for this document before re-adding
        try:
            existing = collection.get(where={"document_name": filename})
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
        except Exception:
            pass

        # Encode in batch
        texts = [c["text"] for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        ids = [str(uuid.uuid4()) for _ in all_chunks]
        metadatas = [{
            "document_name": c["document_name"],
            "page_number": c["page_number"],
            "chunk_index": c["chunk_index"],
            "ingestion_timestamp": datetime.utcnow().isoformat()
        } for c in all_chunks]

        collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

        save_ingested_document(filename, doc_content.file_hash,
                               doc_content.page_count, len(all_chunks))

        stats["processed"] += 1
        stats["chunks_added"] += len(all_chunks)
        stats["documents"].append({
            "filename": filename,
            "status": "processed",
            "pages": doc_content.page_count,
            "chunks": len(all_chunks)
        })
        logger.info(
            f"Ingested {filename}: {doc_content.page_count} pages, {len(all_chunks)} chunks"
        )

    return stats


def get_document_count() -> int:
    try:
        return get_chroma_collection().count()
    except Exception:
        return 0


def get_indexed_documents() -> List[dict]:
    return get_ingested_documents()
