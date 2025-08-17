from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application settings
    app_name: str = "InULearning Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings - 使用 Docker 環境變數
    database_url: str = "postgresql://aipe-tester:aipe-tester@postgres:5432/inulearning"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Redis settings - 使用 Docker 環境變數
    redis_url: str = "redis://redis:6379/0"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8081", "http://localhost:8082", "http://localhost:8083"]
    
    # Security settings
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # 環境變數映射
        fields = {
            'database_url': {'env': 'DATABASE_URL'},
            'jwt_secret_key': {'env': 'SECRET_KEY'},
            'jwt_algorithm': {'env': 'ALGORITHM'},
            'jwt_access_token_expire_minutes': {'env': 'ACCESS_TOKEN_EXPIRE_MINUTES'},
            'redis_url': {'env': 'REDIS_URL'},
            'cors_origins': {'env': 'CORS_ORIGINS'},
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 處理 CORS_ORIGINS 環境變數
        cors_env = os.getenv('CORS_ORIGINS')
        if cors_env and cors_env.strip():
            try:
                self.cors_origins = [origin.strip() for origin in cors_env.split(',')]
            except Exception:
                # 如果解析失敗，使用預設值
                self.cors_origins = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8081", "http://localhost:8082"]


settings = Settings() 