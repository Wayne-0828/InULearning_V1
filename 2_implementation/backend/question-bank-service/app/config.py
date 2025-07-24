from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """應用程式配置設定"""
    
    # 基本設定
    app_name: str = "InULearning Question Bank Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # MongoDB 設定
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "inulearning_question_bank"
    mongodb_questions_collection: str = "questions"
    mongodb_chapters_collection: str = "chapters"
    mongodb_knowledge_points_collection: str = "knowledge_points"
    
    # MinIO 設定
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "question-media"
    minio_secure: bool = False
    
    # Redis 設定
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 1
    
    # API 設定
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]
    
    # 認證設定
    auth_service_url: str = "http://localhost:8001"
    
    # 分頁設定
    default_page_size: int = 20
    max_page_size: int = 100
    
    # 快取設定
    cache_ttl: int = 3600  # 1小時
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 創建全域設定實例
settings = Settings() 