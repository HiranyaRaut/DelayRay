"""
DelayRay Application Configuration Module
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # Security
    JWT_SECRET: str = "supersecret-delayray-dev-key-change-in-production-min32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Demo Mode
    DEMO_MODE: bool = True
    SHOW_SYNTHETIC_BADGE: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./delayray.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://localhost:3000"

    # Ollama Local LLM
    OLLAMA_URL: str = "http://localhost:11434"
    CHAT_MODEL: str = "llama3.1:8b"
    EMBED_MODEL: str = "nomic-embed-text"
    LLM_TIMEOUT_SECONDS: int = 60
    LLM_FALLBACK_MODE: str = "deterministic"

    # Vector store
    VECTOR_STORE_TYPE: str = "faiss"
    VECTOR_INDEX_PATH: str = "./ml_artifacts/remarks_index"

    # Random seed
    RANDOM_SEED: int = 42

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
