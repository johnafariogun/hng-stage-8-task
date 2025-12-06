from fastapi import FastAPI
from routes.documents import router as document_routes

app = FastAPI(title="Document Processing Service")

app.include_router(document_routes)

@app.get("/health")
async def health():
    return {"status": "ok"}

