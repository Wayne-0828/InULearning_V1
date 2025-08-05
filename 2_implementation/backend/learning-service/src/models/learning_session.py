"""
Learning Service Database Models

定義學習服務的資料庫模型
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import ForeignKey

from .base import Base


class LearningSession(Base):
    """學習會話模型"""
    __tablename__ = "learning_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    session_name = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False)
    grade = Column(String(20), nullable=False)
    chapter = Column(String(100))
    publisher = Column(String(20), nullable=False, default='南一')
    difficulty = Column(String(20))
    knowledge_points = Column(ARRAY(Text))
    
    # 會話統計
    question_count = Column(Integer, nullable=False, default=10)
    correct_count = Column(Integer, default=0)
    total_score = Column(DECIMAL(5, 2))
    accuracy_rate = Column(DECIMAL(5, 2))
    time_spent = Column(Integer)  # 秒數
    status = Column(String(20), default='completed')  # active, completed, paused
    session_metadata = Column(JSON)
    
    # 時間戳記
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningSession(id='{self.id}', user_id='{self.user_id}', subject='{self.subject}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "session_name": self.session_name,
            "subject": self.subject,
            "grade": self.grade,
            "chapter": self.chapter,
            "publisher": self.publisher,
            "difficulty": self.difficulty,
            "knowledge_points": self.knowledge_points or [],
            "question_count": self.question_count,
            "correct_count": self.correct_count,
            "total_score": float(self.total_score) if self.total_score else 0.0,
            "accuracy_rate": float(self.accuracy_rate) if self.accuracy_rate else 0.0,
            "time_spent": self.time_spent,
            "status": self.status,
            "session_metadata": self.session_metadata,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LearningRecord(Base):
    """學習記錄模型"""
    __tablename__ = "learning_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    question_id = Column(String(50), nullable=False)
    
    # 答題資訊
    answer = Column(JSON, nullable=False)  # 可以是字串或列表
    correct_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=False, default=0.0)
    time_spent = Column(Integer, nullable=True)  # 秒數
    confidence = Column(Float, nullable=True)  # 信心度 0-1
    
    # 題目資訊
    question_content = Column(Text, nullable=True)
    question_type = Column(String(50), nullable=True)
    subject = Column(String(100), nullable=True)
    chapter = Column(String(200), nullable=True)
    difficulty = Column(String(20), nullable=True)
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningRecord(record_id='{self.record_id}', session_id='{self.session_id}', question_id='{self.question_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "record_id": self.record_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "question_id": self.question_id,
            "answer": self.answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "score": self.score,
            "time_spent": self.time_spent,
            "confidence": self.confidence,
            "question_content": self.question_content,
            "question_type": self.question_type,
            "subject": self.subject,
            "chapter": self.chapter,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserLearningStats(Base):
    """用戶學習統計模型"""
    __tablename__ = "user_learning_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # 總體統計
    total_sessions = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)
    total_time_spent = Column(Integer, nullable=False, default=0)  # 秒數
    
    # 平均統計
    average_score = Column(Float, nullable=False, default=0.0)
    correct_rate = Column(Float, nullable=False, default=0.0)
    
    # 科目統計 (JSON)
    subject_stats = Column(JSON, nullable=True)  # 各科目的詳細統計
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserLearningStats(user_id='{self.user_id}', total_sessions={self.total_sessions})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "total_sessions": self.total_sessions,
            "total_questions": self.total_questions,
            "total_correct": self.total_correct,
            "total_time_spent": self.total_time_spent,
            "average_score": self.average_score,
            "correct_rate": self.correct_rate,
            "subject_stats": self.subject_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }