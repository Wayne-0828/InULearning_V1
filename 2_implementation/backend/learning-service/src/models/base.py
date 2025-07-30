"""
Database Base Model

定義資料庫基礎模型類
"""

from sqlalchemy.ext.declarative import declarative_base

# 創建基礎模型類
Base = declarative_base()

# 導出所有需要的組件
__all__ = ["Base"]