from fastapi import APIRouter, UploadFile, File
import uuid

from services.storage_service import upload_to_s3
from services.document_service import (
    extract_text, save_document_to_db, get_document, save_analysis, ALLOWED_TYPES
)
from services.llm_service import analyze_with_llm
from utils.responses import success, fail
from config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        return fail("Invalid file type. Allowed: pdf, docx, txt")

    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        return fail("File too large (max 5MB)")

    try:
        text = extract_text(content, file.content_type)
    except ValueError as e:
        return fail(str(e))

    doc_id = str(uuid.uuid4())
    s3_key = f"documents/{doc_id}/{file.filename}"

    ok, err = upload_to_s3(s3_key, content, file.content_type)
    if not ok:
        return fail("S3 upload failed", err, 500)

    save_document_to_db(doc_id, file.filename, len(content), file.content_type, s3_key, text)

    return success("Document uploaded", {"id": doc_id, "s3_key": s3_key}, 201)


@router.post("/{doc_id}/analyze")
async def analyze(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        return fail("Document not found", status_code=404)

    if doc["analyzed"]:
        return success("Already analyzed", {
            "summary": doc["summary"],
            "document_type": doc["document_type"],
            "metadata": doc["metadata"]
        })

    analysis = await analyze_with_llm(doc["extracted_text"])
    save_analysis(doc_id, analysis)

    return success("Analysis completed", analysis)


@router.get("/{doc_id}")
async def fetch_document(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        return fail("Document not found", 404)
    return success("Document retrieved", doc)

