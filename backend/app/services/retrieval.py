import logging
from typing import List, Dict, Any

from app.config import settings
from app.services.ingestion import get_embedding_model, get_chroma_collection

logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    """Retrieve top-k most semantically relevant chunks for a query."""
    top_k = top_k or settings.TOP_K_RESULTS

    model = get_embedding_model()
    collection = get_chroma_collection()

    count = collection.count()
    if count == 0:
        logger.warning("Vector store is empty — no documents indexed.")
        return []

    query_embedding = model.encode([query], show_progress_bar=False).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for doc_id, text, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            # ChromaDB cosine distance: 0=identical, 2=opposite → convert to similarity [0,1]
            similarity = max(0.0, 1.0 - (distance / 2.0))
            chunks.append({
                "id": doc_id,
                "text": text,
                "document_name": metadata.get("document_name", "Unknown"),
                "page_number": metadata.get("page_number", 0),
                "chunk_index": metadata.get("chunk_index", 0),
                "similarity": round(similarity, 4),
                "distance": round(distance, 4)
            })

    return chunks


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "and", "but", "or", "so", "yet", "nor", "not", "no", "it", "its",
    "this", "that", "these", "those", "what", "which", "who", "how",
    "when", "where", "why", "i", "me", "my", "we", "our", "you", "your",
    "he", "she", "they", "them", "their", "if", "then", "than", "about",
    "get", "make", "go", "use", "used", "per", "any", "all", "each",
    "also", "must", "only", "same", "other", "more", "just", "being",
}

# Domain-specific terms that always exist in manufacturing docs even for unrelated questions
_MANUFACTURING_NOISE = {
    "plant", "document", "procedure", "process", "material", "operator",
    "manager", "engineer", "supervisor", "inspection", "maintenance",
    "equipment", "machine", "component", "part", "product", "quality",
    "safety", "shift", "work", "operation",
}


def _key_terms(text: str) -> set:
    """Extract meaningful (non-stopword, non-noise) lowercase tokens from text."""
    import re
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return {t for t in tokens if len(t) > 2 and t not in STOPWORDS}


def _subject_terms(query: str) -> set:
    """Extract the specific subject terms that the query is *about* (not just manufacturing)."""
    terms = _key_terms(query)
    # Remove generic manufacturing terms to find specific, non-domain terms
    return terms - _MANUFACTURING_NOISE


def has_lexical_overlap(query: str, chunks: List[Dict[str, Any]],
                        min_matches: int = 1) -> bool:
    """
    Return True if at least min_matches key query subject terms appear in any chunk.
    Uses subject terms (strips common manufacturing noise words) to detect
    queries about topics genuinely absent from the documents.
    """
    subject_terms = _subject_terms(query)
    if not subject_terms:
        # Query is entirely about generic manufacturing concepts — allow
        return True

    all_chunk_text = " ".join(c["text"] for c in chunks).lower()
    matches = sum(1 for t in subject_terms if t in all_chunk_text)
    return matches >= min_matches


def evaluate_evidence(chunks: List[Dict[str, Any]],
                      threshold: float = None,
                      query: str = "") -> tuple:
    """
    Returns (has_evidence: bool, relevant_chunks: List, max_similarity: float).

    Uses two-stage check:
      1. Semantic similarity threshold
      2. Lexical subject-overlap guard: if query is about a topic with no
         subject-term matches in the retrieved chunks, abstain.
    """
    threshold = threshold if threshold is not None else settings.RELEVANCE_THRESHOLD
    if not chunks:
        return False, [], 0.0

    relevant = [c for c in chunks if c["similarity"] >= threshold]
    max_sim = max((c["similarity"] for c in chunks), default=0.0)

    if not relevant:
        return False, [], max_sim

    # Secondary guard: if query subject terms have zero overlap with retrieved docs, abstain
    if query and not has_lexical_overlap(query, relevant):
        logger.info("Lexical subject-overlap guard triggered — query topic absent from chunks.")
        return False, [], max_sim

    return True, relevant, max_sim


def format_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate chunks by (document, page) and format for API response."""
    seen = set()
    sources = []
    for chunk in chunks:
        key = (chunk["document_name"], chunk["page_number"])
        if key not in seen:
            seen.add(key)
            excerpt = chunk["text"]
            if len(excerpt) > 300:
                excerpt = excerpt[:300] + "..."
            sources.append({
                "document_name": chunk["document_name"],
                "page_number": chunk["page_number"],
                "excerpt": excerpt,
                "similarity": chunk["similarity"]
            })
    return sources
