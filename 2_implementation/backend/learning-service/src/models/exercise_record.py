"""
Exercise Record Model

練習記錄模型 - 對應 exercise_records 表
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ExerciseRecord(Base):
    """練習記錄模型"""
    __tablename__ = "exercise_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)
    question_id = Column(String(100), nullable=False)
    
    # 題目資訊
    subject = Column(String(50))
    grade = Column(String(20))
    chapter = Column(String(100))
    publisher = Column(String(20))
    knowledge_points = Column(ARRAY(Text))
    question_content = Column(Text)
    answer_choices = Column(JSON)
    difficulty = Column(String(20))
    question_topic = Column(String(200))
    
    # 答題資訊
    user_answer = Column(Text)
    correct_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score = Column(DECIMAL(5, 2))
    explanation = Column(Text)
    time_spent = Column(Integer)  # 秒數
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExerciseRecord(id='{self.id}', session_id='{self.session_id}', question_id='{self.question_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "user_id": self.user_id,
            "question_id": self.question_id,
            "subject": self.subject,
            "grade": self.grade,
            "chapter": self.chapter,
            "publisher": self.publisher,
            "knowledge_points": self.knowledge_points or [],
            "question_content": self.question_content,
            "answer_choices": self.answer_choices,
            "difficulty": self.difficulty,
            "question_topic": self.question_topic,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "score": float(self.score) if self.score else 0.0,
            "explanation": self.explanation,
            "time_spent": self.time_spent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }