from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import sys
import os

# 添加 shared 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    from database.postgresql import get_postgresql_engine, get_postgresql_session
    # 使用 shared 的 PostgreSQL 配置
    engine = get_postgresql_engine()
    SessionLocal = get_postgresql_session()
except ImportError:
    # 如果無法導入 shared 配置，使用本地配置
    # Create database engine
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """初始化資料庫表"""
    try:
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Auth Service 資料庫表初始化成功")
    except Exception as e:
        print(f"❌ Auth Service 資料庫表初始化失敗: {e}")
        raise


def check_database_connection():
    """檢查資料庫連接"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ 資料庫連接檢查失敗: {e}")
        return False 