from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Required fields with default values from environment
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "fast-gpt")
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GEMINI_API_KEY: str =  os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str =  os.getenv("GEMINI_MODEL")




    # Auto-generate Celery URLs from Redis settings
    @property
    def celery_broker_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def celery_result_backend(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB + 1}"

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Remove Config class since we're using dotenv directly


settings = Settings()