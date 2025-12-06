from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    S3_BUCKET: str = "document-processor"
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    DB_PATH: str = "/app/data/documents.db"

    class Config:
        env_file = ".env"

settings = Settings()

