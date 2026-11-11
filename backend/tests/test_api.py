"""Integration tests for FastAPI endpoints."""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")
os.environ.setdefault("LLM_PROVIDER", "openai")

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)


def make_chunk(sim=0.80):
    return {
        "id": "test-id",
        "document_name": "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf",
        "page_number": 1,
        "text": "Coolant concentration should be 6-8% by refractometer reading.",
        "similarity": sim,
        "chunk_index": 0,
        "distance": 0.4,
    }


class TestHealthEndpoint:
    def test_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_response_structure(self):
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert "llm_provider" in data
        assert "indexed_chunks" in data
        assert "indexed_documents" in data
        assert data["status"] == "healthy"


class TestRootEndpoint:
    def test_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "running"


class TestDocumentsEndpoint:
    def test_returns_document_list(self):
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "count" in data
        assert isinstance(data["documents"], list)


class TestChatEndpoint:
    def test_empty_question_rejected(self):
        response = client.post("/api/chat", json={"question": ""})
        assert response.status_code == 422

    def test_question_too_long_rejected(self):
        response = client.post("/api/chat", json={"question": "x" * 2001})
        assert response.status_code == 422

    def test_valid_response_structure(self):
        with patch("app.services.rag.retrieve_relevant_chunks") as mock_ret, \
             patch("app.services.rag.generate_answer") as mock_gen:
            mock_ret.return_value = [make_chunk(0.80)]
            mock_gen.return_value = "The coolant concentration should be 6-8%."

            response = client.post("/api/chat", json={
                "question": "What is the coolant concentration?"
            })
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "evidence_status" in data
            assert "abstained" in data
            assert "conversation_id" in data

    def test_abstains_on_no_evidence(self):
        low_sim_chunk = make_chunk(0.05)
        with patch("app.services.rag.retrieve_relevant_chunks") as mock_ret:
            mock_ret.return_value = [low_sim_chunk]
            response = client.post("/api/chat", json={
                "question": "What is the weather like in Mumbai today?"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["abstained"] is True
            assert data["evidence_status"] == "insufficient"

    def test_abstains_on_no_chunks(self):
        with patch("app.services.rag.retrieve_relevant_chunks") as mock_ret:
            mock_ret.return_value = []
            response = client.post("/api/chat", json={
                "question": "What is the stock price of Apple?"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["abstained"] is True

    def test_conversation_id_persists(self):
        with patch("app.services.rag.retrieve_relevant_chunks") as mock_ret, \
             patch("app.services.rag.generate_answer") as mock_gen:
            mock_ret.return_value = [make_chunk(0.80)]
            mock_gen.return_value = "Test answer."

            resp1 = client.post("/api/chat", json={"question": "First question"})
            conv_id = resp1.json()["conversation_id"]

            resp2 = client.post("/api/chat", json={
                "question": "Follow-up question",
                "conversation_id": conv_id
            })
            assert resp2.json()["conversation_id"] == conv_id


class TestHistoryEndpoint:
    def test_history_for_new_id_returns_empty(self):
        response = client.get("/api/history/nonexistent-conv-id-xyz")
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []

    def test_history_contains_messages(self):
        with patch("app.services.rag.retrieve_relevant_chunks") as mock_ret, \
             patch("app.services.rag.generate_answer") as mock_gen:
            mock_ret.return_value = []
            mock_gen.return_value = "Answer."

            chat_resp = client.post("/api/chat", json={"question": "History test question"})
            conv_id = chat_resp.json()["conversation_id"]

        hist_resp = client.get(f"/api/history/{conv_id}")
        assert hist_resp.status_code == 200
        messages = hist_resp.json()["messages"]
        assert len(messages) >= 1
        assert any(m["role"] == "user" for m in messages)


class TestUploadEndpoint:
    def test_rejects_non_pdf(self):
        response = client.post("/api/documents/upload",
                               files={"file": ("test.txt", b"not a pdf", "text/plain")})
        assert response.status_code == 400

    def test_rejects_fake_pdf(self):
        response = client.post("/api/documents/upload",
                               files={"file": ("fake.pdf", b"not a real pdf", "application/pdf")})
        assert response.status_code == 400
