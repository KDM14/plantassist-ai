import pytest
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test env vars before any app imports
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")
os.environ.setdefault("LLM_PROVIDER", "openai")

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_pdf_path():
    path = Path(__file__).parent.parent.parent / "data" / "docs" / \
           "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf"
    assert path.exists(), f"Sample PDF not found at {path}"
    return str(path)


@pytest.fixture
def all_docs_dir():
    return str(Path(__file__).parent.parent.parent / "data" / "docs")
