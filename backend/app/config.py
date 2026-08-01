from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "Ludo Royale"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/ludo_royale"
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenRouter
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    ai_model: str = "openrouter/free"
    
    # Game Settings
    turn_timeout_seconds: int = 30
    max_players_per_game: int = 4
    min_players_per_game: int = 2
    ai_replacement_timeout: int = 60  # seconds before AI takes over
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()