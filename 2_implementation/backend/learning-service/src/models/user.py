"""
User Model for Learning Service

由於學習服務需要引用用戶表，但用戶管理在認證服務中，
這裡定義一個簡單的 User 模型僅用於外鍵關聯
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base


class User(Base):
    """用戶模型 - 僅用於外鍵關聯"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='student')
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"