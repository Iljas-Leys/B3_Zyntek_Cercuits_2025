from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/mydb"
    
    # Redis (for future vector DB integration)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Agent TSE"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # AI/LLM (for future implementation)
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "llama3"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()