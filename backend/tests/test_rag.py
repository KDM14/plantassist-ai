"""Tests for the RAG pipeline: retrieval, evidence evaluation, source formatting, LLM logic."""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.retrieval import evaluate_evidence, format_sources, has_lexical_overlap
from app.services.llm import is_safety_question, ABSTAIN_RESPONSE, build_rag_prompt


def make_chunk(doc_name="test.pdf", page=1, text="Sample text content here.",
               similarity=0.75):
    return {
        "id": "test-id",
        "document_name": doc_name,
        "page_number": page,
        "text": text,
        "similarity": similarity,
        "chunk_index": 0,
        "distance": 1.0 - similarity * 2.0,
    }


class TestEvidenceEvaluation:
    def test_sufficient_evidence(self):
        chunks = [make_chunk(similarity=0.70), make_chunk(similarity=0.65)]
        has_ev, relevant, max_sim = evaluate_evidence(chunks, threshold=0.35)
        assert has_ev is True
        assert len(relevant) == 2
        assert max_sim >= 0.65

    def test_insufficient_evidence_low_similarity(self):
        chunks = [make_chunk(similarity=0.10), make_chunk(similarity=0.15)]
        has_ev, relevant, max_sim = evaluate_evidence(chunks, threshold=0.35)
        assert has_ev is False
        assert len(relevant) == 0

    def test_empty_chunks(self):
        has_ev, relevant, max_sim = evaluate_evidence([], threshold=0.35)
        assert has_ev is False
        assert relevant == []
        assert max_sim == 0.0

    def test_mixed_similarity(self):
        chunks = [make_chunk(similarity=0.70), make_chunk(similarity=0.10)]
        has_ev, relevant, max_sim = evaluate_evidence(chunks, threshold=0.35)
        assert has_ev is True
        assert len(relevant) == 1  # Only the high-similarity one

    def test_lexical_overlap_guard_blocks_irrelevant(self):
        # Chunks contain manufacturing text, but query is about salary
        chunks = [make_chunk(text="Coolant must be maintained at proper levels.", similarity=0.70)]
        has_ev, relevant, max_sim = evaluate_evidence(
            chunks, threshold=0.35, query="What is the salary and overtime policy?"
        )
        # "salary" and "overtime" don't appear in the chunk — should abstain
        assert has_ev is False

    def test_lexical_overlap_guard_allows_relevant(self):
        chunks = [make_chunk(text="Coolant concentration must be 6-8%.", similarity=0.70)]
        has_ev, relevant, max_sim = evaluate_evidence(
            chunks, threshold=0.35, query="What is the coolant concentration?"
        )
        # "coolant" and "concentration" appear in chunk — should allow
        assert has_ev is True


class TestSourceFormatting:
    def test_deduplication_by_doc_and_page(self):
        chunks = [
            make_chunk("doc.pdf", 1, "Text A"),
            make_chunk("doc.pdf", 1, "Text B"),  # duplicate page
            make_chunk("doc.pdf", 2, "Text C"),
        ]
        sources = format_sources(chunks)
        assert len(sources) == 2  # deduped

    def test_excerpt_truncated_at_300(self):
        long_text = "word " * 300
        chunks = [make_chunk(text=long_text)]
        sources = format_sources(chunks)
        assert len(sources[0]["excerpt"]) <= 303 + 3  # 300 + "..."
        assert sources[0]["excerpt"].endswith("...")

    def test_short_excerpt_not_truncated(self):
        chunks = [make_chunk(text="Short text.")]
        sources = format_sources(chunks)
        assert sources[0]["excerpt"] == "Short text."

    def test_multiple_docs_preserved(self):
        chunks = [
            make_chunk("doc1.pdf", 1, "Text A"),
            make_chunk("doc2.pdf", 2, "Text B"),
        ]
        sources = format_sources(chunks)
        assert len(sources) == 2
        assert {s["document_name"] for s in sources} == {"doc1.pdf", "doc2.pdf"}


class TestSafetyDetection:
    def test_lockout_question_is_safety(self):
        assert is_safety_question("How do I apply a lockout?")

    def test_loto_is_safety(self):
        assert is_safety_question("What is the LOTO procedure?")

    def test_energized_is_safety(self):
        assert is_safety_question("Is the machine energized?")

    def test_coolant_is_not_safety(self):
        assert not is_safety_question("What is the coolant concentration?")

    def test_spindle_check_is_not_safety(self):
        assert not is_safety_question("How often is spindle runout checked?")

    def test_isolation_is_safety(self):
        assert is_safety_question("How do I isolate the hydraulic circuit?")


class TestAbstainResponse:
    def test_abstain_mentions_documents(self):
        response = ABSTAIN_RESPONSE.lower()
        assert "document" in response or "information" in response

    def test_abstain_advises_escalation(self):
        response = ABSTAIN_RESPONSE.lower()
        assert "supervisor" in response or "specialist" in response


class TestBuildRagPrompt:
    def test_includes_question(self):
        messages = build_rag_prompt("Test question here?", [])
        user_msg = next(m["content"] for m in messages if m["role"] == "user")
        assert "Test question here?" in user_msg

    def test_includes_context_chunks(self):
        chunks = [make_chunk("manual.pdf", 3, "Coolant must be 6-8%")]
        messages = build_rag_prompt("What is coolant concentration?", chunks)
        user_msg = next(m["content"] for m in messages if m["role"] == "user")
        assert "manual.pdf" in user_msg
        assert "Coolant must be 6-8%" in user_msg

    def test_system_prompt_present(self):
        messages = build_rag_prompt("?", [])
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        assert system_msg is not None
        assert len(system_msg["content"]) > 50

    def test_empty_context_handled(self):
        messages = build_rag_prompt("Question?", [])
        user_msg = next(m["content"] for m in messages if m["role"] == "user")
        assert "No relevant document excerpts" in user_msg
