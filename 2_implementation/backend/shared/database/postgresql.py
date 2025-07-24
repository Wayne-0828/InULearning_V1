"""
PostgreSQL 資料庫連接模組
提供 PostgreSQL 資料庫連接和會話管理
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# 建立基礎模型類別
Base = declarative_base()

class PostgreSQLManager:
    """PostgreSQL 資料庫管理器"""
    
    def __init__(self):
        """初始化資料庫管理器"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化資料庫連接"""
        try:
            # 從環境變數取得資料庫配置
            db_host = os.getenv("POSTGRES_HOST", "localhost")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "inulearning")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "password")
            
            # 建立連接字串
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # 建立引擎
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv("SQL_ECHO", "false").lower() == "true"
            )
            
            # 建立會話工廠
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("PostgreSQL 連接初始化成功")
            
        except Exception as e:
            logger.error(f"PostgreSQL 連接初始化失敗: {e}")
            raise
    
    def get_session(self) -> Session:
        """取得資料庫會話"""
        if not self.SessionLocal:
            raise RuntimeError("資料庫會話未初始化")
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self):
        """資料庫會話上下文管理器"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"資料庫操作失敗: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """測試資料庫連接"""
        try:
            with self.get_db_session() as session:
                result = session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"資料庫連接測試失敗: {e}")
            return False
    
    def create_tables(self):
        """建立所有資料表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("PostgreSQL 資料表建立成功")
        except Exception as e:
            logger.error(f"PostgreSQL 資料表建立失敗: {e}")
            raise
    
    def drop_tables(self):
        """刪除所有資料表"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("PostgreSQL 資料表刪除成功")
        except Exception as e:
            logger.error(f"PostgreSQL 資料表刪除失敗: {e}")
            raise
    
    def run_migration(self, migration_file: str) -> bool:
        """執行遷移腳本"""
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            with self.get_db_session() as session:
                # 分割 SQL 語句並執行
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        session.execute(text(statement))
            
            logger.info(f"遷移腳本執行成功: {migration_file}")
            return True
            
        except Exception as e:
            logger.error(f"遷移腳本執行失敗: {migration_file} - {e}")
            return False
    
    def get_database_info(self) -> dict:
        """取得資料庫資訊"""
        try:
            with self.get_db_session() as session:
                # 取得資料庫版本
                version_result = session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # 取得資料表數量
                tables_result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = tables_result.scalar()
                
                # 取得資料庫大小
                size_result = session.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """))
                db_size = size_result.scalar()
                
                return {
                    "version": version,
                    "table_count": table_count,
                    "database_size": db_size,
                    "connection_pool_size": self.engine.pool.size(),
                    "connection_pool_checked_in": self.engine.pool.checkedin(),
                    "connection_pool_checked_out": self.engine.pool.checkedout()
                }
                
        except Exception as e:
            logger.error(f"取得資料庫資訊失敗: {e}")
            return {}

# 全域資料庫管理器實例
postgresql_manager = PostgreSQLManager()

def get_db_session() -> Session:
    """取得資料庫會話的便捷函數"""
    return postgresql_manager.get_session()

@contextmanager
def get_db():
    """資料庫會話上下文管理器的便捷函數"""
    with postgresql_manager.get_db_session() as session:
        yield session 