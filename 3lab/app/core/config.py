from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380
    REDIS_DB: int = 0

settings = Settings()

class WebSocketMessage(BaseModel):
    status: str
    task_id: str
    operation: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None 