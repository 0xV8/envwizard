
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    redis_url: str = "redis://localhost:6379"
    api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
