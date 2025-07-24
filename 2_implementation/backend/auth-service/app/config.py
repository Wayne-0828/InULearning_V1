from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    app_name: str = "InULearning Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://postgres:password@localhost:5432/inulearning_auth"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Security settings
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 