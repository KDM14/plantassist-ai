import hashlib
import logging
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    page_number: int
    text: str
    char_count: int


@dataclass
class DocumentContent:
    filename: str
    file_path: str
    file_hash: str
    page_count: int
    pages: List[PageContent]
    is_scanned: bool = False
    error: Optional[str] = None


def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' \n', '\n', text)
    # Remove standalone page number lines
    text = re.sub(r'^\s*Page \d+\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def extract_pdf(file_path: str) -> DocumentContent:
    path = Path(file_path)
    filename = path.name

    try:
        file_hash = compute_file_hash(file_path)
    except Exception as e:
        return DocumentContent(filename=filename, file_path=file_path, file_hash="",
                               page_count=0, pages=[], error=f"Cannot read file: {e}")

    # Try PyMuPDF first
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        pages = []
        is_scanned = False

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            cleaned = clean_text(text)

            if len(cleaned) < 50 and page_num == 0:
                is_scanned = True

            pages.append(PageContent(
                page_number=page_num + 1,
                text=cleaned,
                char_count=len(cleaned)
            ))
        doc.close()

        return DocumentContent(
            filename=filename, file_path=file_path, file_hash=file_hash,
            page_count=len(pages), pages=pages, is_scanned=is_scanned
        )
    except Exception as e:
        logger.warning(f"PyMuPDF failed for {filename}: {e}, trying pypdf fallback")

    # Fallback: pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            cleaned = clean_text(text)
            pages.append(PageContent(page_number=i + 1, text=cleaned, char_count=len(cleaned)))
        return DocumentContent(
            filename=filename, file_path=file_path, file_hash=file_hash,
            page_count=len(pages), pages=pages
        )
    except Exception as e2:
        return DocumentContent(filename=filename, file_path=file_path, file_hash=file_hash,
                               page_count=0, pages=[], error=str(e2))


def chunk_text(text: str, page_number: int, doc_name: str,
               chunk_size: int = 500, overlap: int = 100) -> List[dict]:
    """Split text into overlapping word-based chunks."""
    chunks = []
    if not text or len(text.strip()) < 20:
        return chunks

    words = text.split()
    if not words:
        return chunks

    chunk_index = 0
    step = max(1, chunk_size - overlap)
    i = 0

    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text_str = " ".join(chunk_words)

        if len(chunk_text_str.strip()) > 20:
            chunks.append({
                "text": chunk_text_str,
                "page_number": page_number,
                "document_name": doc_name,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

        i += step

    return chunks
