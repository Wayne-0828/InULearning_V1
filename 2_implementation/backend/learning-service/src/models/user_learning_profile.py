"""
User Learning Profile Model

用戶學習檔案模型 - 對應 user_learning_profiles 表
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import ForeignKey, Text

from .base import Base


class UserLearningProfile(Base):
    """用戶學習檔案模型"""
    __tablename__ = "user_learning_profiles"
    
    user_id = Column(Integer, primary_key=True)
    current_grade = Column(String(20))
    preferred_subjects = Column(ARRAY(Text))
    preferred_publishers = Column(ARRAY(Text))
    
    # 知識點追蹤
    strength_knowledge_points = Column(ARRAY(Text))  # 強項知識點
    weakness_knowledge_points = Column(ARRAY(Text))   # 弱項知識點
    
    # 統計數據
    total_practice_time = Column(Integer, default=0)  # 總練習時間（秒）
    total_sessions = Column(Integer, default=0)       # 總練習會話數
    total_questions = Column(Integer, default=0)      # 總答題數
    correct_questions = Column(Integer, default=0)    # 總答對數
    overall_accuracy = Column(DECIMAL(5, 2), default=0)  # 整體正確率
    
    # 學習偏好
    preferred_difficulty = Column(String(20), default='normal')
    learning_preferences = Column(JSON)  # 其他學習偏好設置
    
    # 時間追蹤
    last_practice_date = Column(Date)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserLearningProfile(user_id={self.user_id}, current_grade='{self.current_grade}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "user_id": self.user_id,
            "current_grade": self.current_grade,
            "preferred_subjects": self.preferred_subjects or [],
            "preferred_publishers": self.preferred_publishers or [],
            "strength_knowledge_points": self.strength_knowledge_points or [],
            "weakness_knowledge_points": self.weakness_knowledge_points or [],
            "total_practice_time": self.total_practice_time,
            "total_sessions": self.total_sessions,
            "total_questions": self.total_questions,
            "correct_questions": self.correct_questions,
            "overall_accuracy": float(self.overall_accuracy) if self.overall_accuracy else 0.0,
            "preferred_difficulty": self.preferred_difficulty,
            "learning_preferences": self.learning_preferences,
            "last_practice_date": self.last_practice_date.isoformat() if self.last_practice_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }