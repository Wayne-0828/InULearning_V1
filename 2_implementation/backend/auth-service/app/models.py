from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
import sys
import os

# 添加 shared 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    from models.user import User as SharedUser
    from models.user_profile import UserProfile as SharedUserProfile
except ImportError:
    # 如果無法導入 shared 模型，使用本地定義
    SharedUser = None
    SharedUserProfile = None


class UserRole(str, enum.Enum):
    student = "student"
    parent = "parent"
    teacher = "teacher"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role.value if self.role else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens") 