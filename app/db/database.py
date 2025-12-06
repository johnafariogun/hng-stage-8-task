import os
import sqlite3
from datetime import datetime
from config import settings
from utils.logger import logger

DB_NAME = settings.DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                file_size INTEGER,
                content_type TEXT,
                s3_key TEXT,
                extracted_text TEXT,
                created_at TEXT,
                analyzed BOOLEAN DEFAULT 0,
                summary TEXT,
                document_type TEXT,
                metadata TEXT
            )
        ''')
        conn.commit()

logger.info("Initializing database")
init_db()

