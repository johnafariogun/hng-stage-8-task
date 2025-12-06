
# Document Processing Service

A containerized API for uploading documents (PDF, DOCX, TXT), extracting their text content, storing them in object storage (MinIO / S3‑compatible) and SQLite, then optionally analyzing them via an LLM (through OpenRouter API).

## 🚀 What It Does

- Accepts file uploads (PDF, DOCX, TXT) via HTTP.  
- Extracts text from documents, stores the file in S3-compatible storage, and saves metadata + extracted text in a SQLite database.  
- Offers endpoints to retrieve documents and metadata, and to trigger automatic analysis (summary, type detection, metadata extraction) using an LLM.  
- Fully containerized: deployed with Docker + docker-compose for easy setup and portability.

## 📦 Tech Stack

| Component | Purpose |
|----------|---------|
| FastAPI + Uvicorn | Web framework and ASGI server to handle API requests asynchronously |
| SQLite | Lightweight local database for document metadata and extracted text |
| MinIO (S3‑compatible) | Object storage for uploaded files; self‑hosted so no external cloud vendor needed |
| Boto3 | Python SDK to interact with S3/MinIO for file uploads/downloads |
| OpenRouter API | Gateway to LLM model(s) used for document analysis (summary, metadata extraction) |
| Docker & docker-compose | Containerization for consistent deployment and easy environment setup |

## 📁 Project Structure


```
.
├── Dockerfile
├── docker-compose.yml
├── config.py
├── main.py
├── db/
│   └── database.py
├── routes/
│   └── documents.py
├── services/
│   ├── document_service.py
│   ├── llm_service.py
│   └── storage_service.py
└── utils/
└── responses.py

```````
- **config.py** — settings and configuration (e.g. S3 bucket name, DB path, API keys).  
- **db/** — SQLite initialization and database utilities.  
- **services/** — core logic: file extraction, S3 uploads, LLM analysis.  
- **routes/** — API route definitions for upload, retrieval, analysis.  
- **utils/** — helper modules (e.g. standardized responses).  
- **Dockerfile + docker-compose.yml** — container and orchestration configuration for app + MinIO.

## ✅ Getting Started (Local / Development)

> Make sure you have Docker and docker-compose installed.

1. Clone the repository  
   ```bash
   git clone https://github.com/johnafariogun/hng-stage-8-task.git
   cd hng-stage-8-task
    ```

2. Create a `.env` file (in repo root) with required environment variables, e.g.:

   ```
   OPENROUTER_API_KEY=your_openrouter_key
   AWS_ACCESS_KEY_ID=minioadmin
   AWS_SECRET_ACCESS_KEY=minioadmin
   ```

3. Start the services

   ```
   docker compose up --build -d
   ```

4. Visit the API at: `http://localhost:8000`
   
     — Use the endpoints documented below to upload or manage documents.
  
      ## 🔧 API Endpoints (Summary)
      
      | Method   | Endpoint                      | Description                                                        |
      | -------- | ----------------------------- | ------------------------------------------------------------------ |
      | **POST** | `/documents/upload`           | Upload a new document (PDF / DOCX / TXT)                           |
      | **POST** | `/documents/{doc_id}/analyze` | Trigger LLM-based analysis on an uploaded document                 |
      | **GET**  | `/documents/{doc_id}`         | Retrieve stored document metadata, extracted text, analysis result |
      
      *All responses follow a JSON schema with `status`, `message`, and `data` or `error` fields.*
      
      ## ⚙️ Configuration
      
      You can configure the following (via `config.py` or environment variables):
      
      * S3/MinIO bucket name
      * S3 endpoint URL (e.g. for MinIO)
      * AWS credentials (or MinIO credentials)
      * SQLite database path
      * Maximum file upload size
      
      ## 📝 License & Contribution
      
      Feel free to open issues or PRs. Contributions, discussions, and improvements are welcome.
      
    
