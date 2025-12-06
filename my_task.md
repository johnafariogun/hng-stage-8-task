Task 4:
AI Document Summarization + Metadata Extraction Workflow
Problem
Build a service that accepts a PDF or DOCX file, extracts text, sends it to an LLM on OpenRouter, and returns:
A concise summary
Detected document type (invoice, CV, report, letter, etc.)
Extracted metadata (date, sender, total amount, etc.)
Requirements
/documents/upload
Accept PDF (max 5MB).
Store raw file in S3/Minio.
Extract text using a library
Save text + metadata in DB.
/documents/{id}/analyze
Send extracted text to an LLM on OpenRouter (e.g., gpt-4o-mini or any free model).
Save LLM output to DB (summary, type, attributes).
/documents/{id}
Return combined data: file info, text, summary, metadata.