"""
Configuration Management

This module handles configuration settings for the AI analysis service.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 應用程式設定
    app_name: str = "AI Analysis Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 資料庫設定
    database_url: str = "postgresql://user:password@localhost:5432/inulearning"
    
    # AI 服務設定
    gemini_api_key: str = ""
    
    # Milvus 向量資料庫設定
    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    
    # Redis 設定
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # 服務設定
    host: str = "0.0.0.0"
    port: int = 8004
    service_host: str = "0.0.0.0"
    service_port: int = 8004
    
    # 日誌設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 安全設定
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全域設定實例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """獲取設定實例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings():
    """重新載入設定"""
    global _settings
    _settings = None
    return get_settings() 