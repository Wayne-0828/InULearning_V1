"""
Database Connection Management

This module handles database connections and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys
import os
from .config import get_settings

# 添加 shared 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

# 獲取設定
settings = get_settings()

# 使用本地配置，避免 shared 配置的連接問題
print("⚠️ 使用本地資料庫配置")

# 創建資料庫引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 本地 Redis 配置
import redis.asyncio as redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url)

# 創建基礎模型類
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化資料庫"""
    try:
        # 創建所有表格
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL 資料庫表創建成功")
    except Exception as e:
        print(f"❌ PostgreSQL 資料庫表創建失敗: {e}")
        raise


def get_db_session() -> Session:
    """獲取資料庫會話（非生成器版本）"""
    return SessionLocal()


async def get_redis_connection():
    """獲取 Redis 連接"""
    return redis_client


async def check_redis_connection() -> bool:
    """檢查 Redis 連接"""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        print(f"❌ Redis 連接檢查失敗: {e}")
        return False


def check_postgresql_connection() -> bool:
    """檢查 PostgreSQL 連接"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL 連接檢查失敗: {e}")
        return False 