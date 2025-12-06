import io
import json
import uuid
import sqlite3
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
from db.database import DB_NAME
from utils.logger import logger

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

def extract_text(file_bytes: bytes, content_type: str) -> str:
    try:
        stream = io.BytesIO(file_bytes)

        if content_type == "application/pdf":
            reader = PdfReader(stream)
            return "\n".join([p.extract_text() or "" for p in reader.pages])

        elif content_type == "text/plain":
            return file_bytes.decode("utf-8", errors="ignore")

        else:  # docx
            doc = Document(stream)
            return "\n".join([p.text for p in doc.paragraphs])

    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise ValueError("Could not extract text from document")

def save_document_to_db(doc_id, filename, size, content_type, s3_key, extracted_text):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO documents
            (id, filename, file_size, content_type, s3_key, extracted_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, filename, size, content_type, s3_key,
            extracted_text, datetime.utcnow().isoformat()
        ))

def get_document(doc_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return dict(row) if row else None

def save_analysis(doc_id, analysis: dict):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            UPDATE documents
            SET analyzed = 1,
                summary = ?,
                document_type = ?,
                metadata = ?
            WHERE id = ?
        """, (
            analysis.get("summary"),
            analysis.get("document_type"),
            json.dumps(analysis.get("metadata")),
            doc_id
        ))

