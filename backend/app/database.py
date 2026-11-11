import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from app.config import settings


def get_db():
    Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT,
            evidence_status TEXT,
            abstained INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );
        CREATE TABLE IF NOT EXISTS ingested_documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            file_hash TEXT NOT NULL,
            page_count INTEGER,
            chunk_count INTEGER,
            ingested_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def save_message(conversation_id: str, role: str, content: str,
                 sources=None, evidence_status=None, abstained=False):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    cursor.execute(
        "INSERT OR IGNORE INTO conversations (id, created_at, updated_at) VALUES (?, ?, ?)",
        (conversation_id, now, now)
    )
    cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))

    msg_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO messages (id, conversation_id, role, content, sources, evidence_status, abstained, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (msg_id, conversation_id, role, content,
          json.dumps(sources) if sources else None,
          evidence_status, 1 if abstained else 0, now))
    conn.commit()
    conn.close()
    return msg_id


def get_conversation_history(conversation_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, sources, evidence_status, abstained, created_at
        FROM messages WHERE conversation_id = ? ORDER BY created_at ASC
    """, (conversation_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "role": row["role"],
        "content": row["content"],
        "sources": json.loads(row["sources"]) if row["sources"] else None,
        "evidence_status": row["evidence_status"],
        "abstained": bool(row["abstained"]),
        "created_at": row["created_at"]
    } for row in rows]


def get_ingested_documents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingested_documents ORDER BY ingested_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_ingested_document(filename, file_hash, page_count, chunk_count):
    conn = get_db()
    cursor = conn.cursor()
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO ingested_documents (id, filename, file_hash, page_count, chunk_count, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (doc_id, filename, file_hash, page_count, chunk_count, now))
    conn.commit()
    conn.close()


def get_document_hash(filename):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_hash FROM ingested_documents WHERE filename = ?", (filename,))
    row = cursor.fetchone()
    conn.close()
    return row["file_hash"] if row else None
