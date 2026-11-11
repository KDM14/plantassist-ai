"""Tests for PDF extraction and chunking pipeline."""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.pdf_extractor import extract_pdf, chunk_text, clean_text, compute_file_hash

DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "docs"


class TestFileHash:
    def test_hash_is_deterministic(self, sample_pdf_path):
        h1 = compute_file_hash(sample_pdf_path)
        h2 = compute_file_hash(sample_pdf_path)
        assert h1 == h2

    def test_hash_is_sha256(self, sample_pdf_path):
        h = compute_file_hash(sample_pdf_path)
        assert len(h) == 64  # SHA-256 hex string


class TestTextCleaning:
    def test_removes_excess_whitespace(self):
        result = clean_text("hello   world")
        assert "   " not in result

    def test_normalises_newlines(self):
        result = clean_text("line1\r\nline2\r\nline3")
        assert "\r" not in result

    def test_collapses_blank_lines(self):
        result = clean_text("a\n\n\n\n\nb")
        assert "\n\n\n" not in result

    def test_empty_string(self):
        result = clean_text("")
        assert result == ""


class TestPdfExtraction:
    def test_extract_maintenance_manual(self, sample_pdf_path):
        result = extract_pdf(sample_pdf_path)
        assert result.error is None, f"Extraction error: {result.error}"
        assert result.page_count == 2
        assert len(result.pages) == 2
        assert result.filename == "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf"

    def test_page_numbers_are_correct(self, sample_pdf_path):
        result = extract_pdf(sample_pdf_path)
        assert result.pages[0].page_number == 1
        assert result.pages[1].page_number == 2

    def test_maintenance_content_present(self, sample_pdf_path):
        result = extract_pdf(sample_pdf_path)
        full_text = " ".join(p.text for p in result.pages).lower()
        assert "tx-200" in full_text
        assert "hydraulic" in full_text
        assert "coolant" in full_text

    def test_file_hash_in_result(self, sample_pdf_path):
        result = extract_pdf(sample_pdf_path)
        assert len(result.file_hash) == 64

    def test_all_docs_extractable(self, all_docs_dir):
        for pdf in Path(all_docs_dir).glob("*.pdf"):
            if "sample" in pdf.name.lower():
                continue
            result = extract_pdf(str(pdf))
            assert result.error is None, f"Failed to extract {pdf.name}: {result.error}"
            assert result.page_count > 0, f"Zero pages in {pdf.name}"

    def test_invalid_pdf_handled_gracefully(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"this is not a pdf")
        result = extract_pdf(str(bad))
        # Should return an error or empty pages, not raise
        assert result.error is not None or result.page_count == 0


class TestChunking:
    def test_chunks_generated(self):
        text = " ".join(f"word{i}" for i in range(600))
        chunks = chunk_text(text, page_number=1, doc_name="test.pdf",
                            chunk_size=100, overlap=20)
        assert len(chunks) > 1

    def test_chunk_metadata(self):
        text = " ".join(f"word{i}" for i in range(200))
        chunks = chunk_text(text, page_number=3, doc_name="manual.pdf",
                            chunk_size=50, overlap=10)
        for chunk in chunks:
            assert chunk["page_number"] == 3
            assert chunk["document_name"] == "manual.pdf"
            assert len(chunk["text"]) > 0

    def test_overlap_creates_multiple_chunks(self):
        text = " ".join(f"word{i}" for i in range(300))
        chunks = chunk_text(text, page_number=1, doc_name="test.pdf",
                            chunk_size=100, overlap=50)
        assert len(chunks) >= 2

    def test_short_text_handled(self):
        chunks = chunk_text("short", page_number=1, doc_name="test.pdf",
                            chunk_size=100, overlap=10)
        assert len(chunks) == 0  # Too short (<20 chars)

    def test_empty_text_handled(self):
        chunks = chunk_text("", page_number=1, doc_name="test.pdf",
                            chunk_size=100, overlap=10)
        assert chunks == []
