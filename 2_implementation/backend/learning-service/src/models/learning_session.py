"""
Learning Service Database Models

定義學習服務的資料庫模型
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class LearningSession(Base):
    """學習會話模型"""
    __tablename__ = "learning_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    grade = Column(String(50), nullable=True)
    chapter = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default="active")  # active, completed, paused, cancelled
    
    # 會話參數
    question_count = Column(Integer, nullable=False, default=10)
    difficulty = Column(String(20), nullable=True, default="medium")
    time_limit = Column(Integer, nullable=True)  # 分鐘
    
    # 會話數據 (JSON)
    questions = Column(JSON, nullable=True)  # 題目列表
    answers = Column(JSON, nullable=True)    # 答案記錄
    results = Column(JSON, nullable=True)    # 結果記錄
    
    # 統計資訊
    total_questions = Column(Integer, nullable=False, default=0)
    answered_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    total_score = Column(Float, nullable=True)
    time_spent = Column(Integer, nullable=True)  # 秒數
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<LearningSession(session_id='{self.session_id}', user_id='{self.user_id}', subject='{self.subject}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "subject": self.subject,
            "grade": self.grade,
            "chapter": self.chapter,
            "status": self.status,
            "question_count": self.question_count,
            "difficulty": self.difficulty,
            "time_limit": self.time_limit,
            "questions": self.questions,
            "answers": self.answers,
            "results": self.results,
            "total_questions": self.total_questions,
            "answered_questions": self.answered_questions,
            "correct_answers": self.correct_answers,
            "total_score": self.total_score,
            "time_spent": self.time_spent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
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