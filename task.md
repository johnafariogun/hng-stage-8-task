Hello Backend Engineers! I have your Stage 7 feast ready. Let’s see if you can finish it,  I heard your mentors wrote it with one eye closed. They’ve given you five options to keep your hands full!
Check below for your preferred task and submit your code by 6th December, 2:59 PM WAT via this submission link
Task 1:
Google Sign-In & Paystack Payment — Task Requirements
The goal is to test your ability to build simple backend endpoints, integrate with third‑party services, and understand basic authentication and payment flows.
Aim
Implement backend-only Google Sign-In and Paystack payment functionalities, exposing secure, well-defined API endpoints that authenticate users, initiate payments, and provide reliable transaction status updates.
Objectives
Understand how Google sign‑in works at a basic level.
Make simple backend endpoints that call Google and Paystack.
Save basic information to the database.
Handle payment initiation and check payment status.
Scope (In-Scope)
Backend-only endpoints and flows — no UI work required.
Database schema for storing users and payments / transactions.
Integration with Google OAuth 2.0 (server-side flow using client credentials).
Integration with Paystack to create transactions and get transaction status using webhook or paystack’s verify transaction endpoint.
Out of Scope
Frontend integration & UI components.
Alternative payment providers other than Paystack.
High-Level Flow (Easy Description)
Google Sign‑In
The user hits an endpoint.
They get redirected to Google to log in.
Google sends a code back to your callback endpoint.
Your server exchanges that code for the user’s info.
You save the user in the database.
Paystack Payment
The user hits your “start payment” endpoint.
Your server calls Paystack to initialize a transaction.
Paystack sends back an authorization link.
You return that link to the user.
To check status, your server can:
receive a webhook from Paystack, or
call Paystack’s verify endpoint when someone asks.
API Endpoints (Specification)
1. Trigger Google sign-in flow
GET /auth/google
Purpose: Return a redirect (302) to Google OAuth consent page or provide the URL in JSON.
Response (redirect): 302 -> Google OAuth URL
Response (JSON option): 200 { "google_auth_url": "https://accounts.google.com/...." }
Errors: 400 invalid redirect, 500 on internal error
2. Google OAuth callback
GET /auth/google/callback
Purpose:
Exchange code for access token (server-to-server call to Google's token endpoint).
Fetch userinfo from Google (openid, email, name, picture, etc.).
Create or update a User record in the DB.
Success Response: 200 JSON { "user_id": "...", "email": "...", "name": "..." }
Errors: 400 missing code, 401 invalid code, 500 provider error
3. Initiate Paystack payment
POST /payments/paystack/initiate
Body JSON (example):
 {
   "amount": 5000,  // amount in Kobo (lowest currency unit)
 }
Steps:
Validate user and amount.
Call Paystack Initialize Transaction API with secret key.
Persist transaction with reference and initial status pending.
Response: 201
{ 
  "reference": "...", 
  "authorization_url": "https://paystack.co/checkout/...." 
}
Errors: 400 invalid input, 402 payment initiation failed by Paystack, 500
4. Webhook endpoint (optional but recommended)
POST /payments/paystack/webhook
Purpose: Receive transaction updates from Paystack.
Security: Validate Paystack signature header (e.g. x-paystack-signature) using configured webhook secret.
Steps:
Verify signature.
Parse event payload; find transaction reference.
Update transaction status in DB (success, failed, pending, etc.).
Response: 200
{"status": true}
Errors: 400 invalid signature, 500 server error
5. Check transaction status (on-demand)
GET /payments/{reference}/status
Purpose: Return the latest status for reference.
Behavior: Return DB status. If missing or caller requests refresh=true, call Paystack verify endpoint to fetch live status and update DB.
Response: 200
{ 
  "reference": "...", 
  "status": "success|failed|pending", 
  "amount": 5000, 
  "paid_at": "..." 
}
Security Considerations (Simple)
Don’t expose your secret keys.
Make sure only Google redirects back to your callback.
Verify Paystack webhooks so strangers can’t fake payment updates.
Error Handling & Idempotency
Use the reference as idempotency key for Paystack transactions. If duplicate initiation is detected, return the existing transaction to the initiator of the transaction only.
Return clear error codes and messages.
Task 2:
Build an Upload Service With Background Image Processing
Problem
An endpoint where users upload images, but processing happens async.
Requirements
/upload for file upload (S3 or local Minio)
Publish a job to Celery / BullMQ / Sidekiq-style worker
Worker performs:
Resize
Compress
Generate a thumbnail
Provide /upload/{id}/status
Provide /upload/{id}/result with processed URLs
Task 3:
Build a Mini Authentication + API Key System for Service-to-Service Access
Problem
Build an auth system that supports:
User login via JWT
Service-to-Service access via API keys
Requirements
/auth/signup, /auth/login
/keys/create to generate API keys
Middleware detects:
Bearer token (user)
API key (service)
Protect routes based on access type
Add expiration or revocation for API keys
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
Task 5:
AI-Powered Document Search & RAG Query Service (Vector DB + OpenRouter)
Problem
Build a backend service that ingests documents, breaks them into chunks, embeds them using an OpenRouter embedding model, stores them in a vector database (Pinecone or ChromaDB), and exposes an endpoint that answers user questions using RAG.
Requirements
/documents/upload
Accept PDF, DOCX, or TXT
Extract clean text
Chunk the text (e.g., 300–600 tokens)
Generate embeddings via OpenRouter
Store chunks + embeddings in Pinecone or ChromaDB
Record document metadata in DB
/query
Embed user question
Run vector search to fetch top-K relevant chunks
Build RAG prompt using retrieved context
Call an OpenRouter LLM to generate an answer
Return:
the answer
list of chunks used
similarity scores
/documents
List uploaded documents and chunk counts
/documents/:id
Return extracted text, chunks, and metadata
Please note that we will check if your team has done something similar before. Do not work on a task your team has already completed. I will decide what counts as prior work, as you know your team’s product better than I do.
Rest assured, we will be able to tell.