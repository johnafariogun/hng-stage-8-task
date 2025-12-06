import os
import io
import uuid
import json
import sqlite3
import asyncio
import boto3
import httpx
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from PyPDF2 import PdfReader
from docx import Document
from botocore.exceptions import ClientError

# --- Configuration ---
class Settings(BaseSettings):
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    S3_BUCKET: str = "document-processor"
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(title="Document Processing Service")

# --- Database & S3 Setup ---
DB_NAME = "documents.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS documents
                     (id TEXT PRIMARY KEY,
                      filename TEXT,
                      file_size INTEGER,
                      content_type TEXT,
                      s3_key TEXT,
                      extracted_text TEXT,
                      created_at TEXT,
                      analyzed BOOLEAN DEFAULT 0,
                      summary TEXT,
                      document_type TEXT,
                      metadata TEXT)''')
        conn.commit()

init_db()

def get_s3_client():
    try:
        return boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    except Exception as e:
        print(f"S3 Client Error: {e}")
        return None

s3_client = get_s3_client()

# --- Response Wrappers ---
def success_response(message: str, data: Optional[Any] = None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "status": "success",
            "status_code": status_code,
            "message": message,
            "data": data or {}
        })
    )

def fail_response(message: str, error: Optional[Any] = None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "status": "fail",
            "status_code": status_code,
            "message": message,
            "error": error or {}
        })
    )

# --- Utilities ---
def extract_text(file_content: bytes, content_type: str) -> str:
    try:
        file_stream = io.BytesIO(file_content)
        if content_type == 'application/pdf':
            reader = PdfReader(file_stream)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else: # docx
            doc = Document(file_stream)
            text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f" extraction failed: {str(e)}")

async def analyze_with_llm(text: str) -> Dict[str, Any]:
    prompt = f"""
    Analyze the document text below. Return ONLY valid JSON.
    Fields required:
    1. summary (concise, 2 sentences)
    2. document_type (invoice, CV, report, letter, contract, other)
    3. metadata (JSON object with date, sender, recipient, total_amount, currency, etc.)
    
    Text: {text[:3500]}
    """
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini", # or "meta-llama/llama-3.1-8b-instruct:free"
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            
            # Clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content.strip())
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback
            return {"summary": "Analysis failed", "document_type": "unknown", "metadata": {}}

# --- Endpoints ---

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    # 1. Validation
    if file.content_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return fail_response("Invalid file type. Only PDF and DOCX allowed.", status_code=400)
    
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        return fail_response(f"File too large. Max {settings.MAX_FILE_SIZE/1024/1024}MB", status_code=400)

    # 2. Extract Text
    try:
        extracted_text = extract_text(file_content, file.content_type)
        if not extracted_text:
            return fail_response("No text could be extracted.", status_code=400)
    except ValueError as e:
        return fail_response(str(e), status_code=400)

    # 3. Upload to S3
    doc_id = str(uuid.uuid4())
    s3_key = f"documents/{doc_id}/{file.filename}"
    
    if s3_client:
        try:
            s3_client.put_object(Bucket=settings.S3_BUCKET, Key=s3_key, Body=file_content, ContentType=file.content_type)
        except ClientError as e:
            return fail_response("S3 upload failed", error=str(e), status_code=500)

    # 4. Save to DB
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO documents (id, filename, file_size, content_type, s3_key, extracted_text, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (doc_id, file.filename, len(file_content), file.content_type, s3_key, extracted_text, datetime.utcnow().isoformat())
        )
    
    return success_response(
        "Document uploaded successfully",
        {"id": doc_id, "filename": file.filename, "s3_key": s3_key},
        status_code=201
    )

@app.post("/documents/{doc_id}/analyze")
async def analyze_document(doc_id: str):
    # 1. Fetch Document
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    
    if not row:
        return fail_response("Document not found", status_code=404)
    
    doc = dict(row)
    
    # Return early if already analyzed
    if doc['analyzed']:
        return success_response("Document retrieved (already analyzed)", {
            "summary": doc['summary'],
            "document_type": doc['document_type'],
            "metadata": json.loads(doc['metadata']) if doc['metadata'] else {}
        })

    # 2. Analyze
    analysis = await analyze_with_llm(doc['extracted_text'])
    
    # 3. Update DB
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''UPDATE documents SET analyzed = 1, summary = ?, document_type = ?, metadata = ? WHERE id = ?''',
            (analysis.get('summary'), analysis.get('document_type'), json.dumps(analysis.get('metadata')), doc_id)
        )

    return success_response("Analysis complete", analysis)

@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
        
    if not row:
        return fail_response("Document not found", status_code=404)

    doc = dict(row)
    # Parse metadata string back to JSON for response
    if doc.get('metadata'):
        try:
            doc['metadata'] = json.loads(doc['metadata'])
        except:
            doc['metadata'] = {}

    return success_response("Document retrieved", doc)

@app.get("/health")
async def health_check():
    return success_response("System healthy", {"timestamp": datetime.utcnow().isoformat()})