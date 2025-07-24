"""
資料庫連接和初始化工具

提供 PostgreSQL 和 MongoDB 資料庫連接池和初始化功能
"""

import os
import logging
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# 添加 shared 目錄到 Python 路徑
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ..models.base import Base

logger = logging.getLogger(__name__)

# 嘗試導入 shared 資料庫配置
try:
    from database.postgresql import get_postgresql_engine, get_postgresql_session
    from database.mongodb import get_mongodb_client, get_mongodb_database
    from database.redis import get_redis_client
    
    # 使用 shared 的 PostgreSQL 配置
    engine = get_postgresql_engine()
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 使用 shared 的 MongoDB 配置
    mongodb_client = get_mongodb_client()
    mongodb_database = get_mongodb_database()
    
    # 使用 shared 的 Redis 配置
    redis_client = get_redis_client()
    
    logger.info("✅ 成功導入 shared 資料庫配置")
    
except ImportError as e:
    logger.warning(f"⚠️ 無法導入 shared 資料庫配置，使用本地配置: {e}")
    
    # 資料庫配置
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/inulearning"
    )

    # 創建異步引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        poolclass=NullPool if os.getenv("TESTING", "false").lower() == "true" else None,
        pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "30")),
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # 創建異步會話工廠
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 本地 MongoDB 配置
    from motor.motor_asyncio import AsyncIOMotorClient
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_database_name = os.getenv("MONGODB_DATABASE", "inulearning")
    
    mongodb_client = AsyncIOMotorClient(mongodb_url)
    mongodb_database = mongodb_client[mongodb_database_name]
    
    # 本地 Redis 配置
    import redis.asyncio as redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """獲取 PostgreSQL 資料庫會話"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_mongodb_collection(collection_name: str):
    """獲取 MongoDB 集合"""
    return mongodb_database[collection_name]


async def get_redis_connection():
    """獲取 Redis 連接"""
    return redis_client


async def init_database():
    """初始化資料庫"""
    try:
        # 創建 PostgreSQL 表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ PostgreSQL 資料庫表創建成功")
        
        # 測試 MongoDB 連接
        await mongodb_client.admin.command('ping')
        logger.info("✅ MongoDB 連接成功")
        
        # 測試 Redis 連接
        await redis_client.ping()
        logger.info("✅ Redis 連接成功")
        
    except Exception as e:
        logger.error(f"❌ 資料庫初始化失敗: {e}")
        raise


async def close_database():
    """關閉資料庫連接"""
    try:
        await engine.dispose()
        mongodb_client.close()
        await redis_client.close()
        logger.info("✅ 資料庫連接已關閉")
    except Exception as e:
        logger.error(f"❌ 關閉資料庫連接時發生錯誤: {e}")


async def check_database_connection() -> bool:
    """檢查資料庫連接"""
    try:
        # 檢查 PostgreSQL
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # 檢查 MongoDB
        await mongodb_client.admin.command('ping')
        
        # 檢查 Redis
        await redis_client.ping()
        
        return True
    except Exception as e:
        logger.error(f"❌ 資料庫連接檢查失敗: {e}")
        return False 