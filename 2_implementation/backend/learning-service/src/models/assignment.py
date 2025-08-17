"""
作業資料庫模型

定義作業相關的資料庫表結構
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from .base import Base


class Assignment(Base):
    """作業模型"""
    __tablename__ = "assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, comment="作業標題")
    description = Column(Text, nullable=False, comment="作業描述")
    subject = Column(String(50), nullable=False, comment="科目")
    grade = Column(String(20), nullable=False, comment="年級")
    chapter = Column(String(100), comment="章節")
    due_date = Column(DateTime, comment="截止日期")
    time_limit = Column(Integer, comment="限時（分鐘）")
    question_count = Column(Integer, nullable=False, default=10, comment="題目數量")
    difficulty = Column(String(20), default="medium", comment="難度")
    shuffle_questions = Column(Boolean, default=True, comment="題目亂序")
    shuffle_options = Column(Boolean, default=True, comment="選項亂序")
    
    # 關聯
    teacher_id = Column(Integer, nullable=False, comment="創建教師ID")
    class_ids = Column(ARRAY(String), comment="指派班級ID列表")
    
    # 統計資訊
    status = Column(String(20), default="active", comment="狀態: active, inactive, archived")
    total_students = Column(Integer, default=0, comment="總學生數")
    submitted_count = Column(Integer, default=0, comment="已提交數")
    graded_count = Column(Integer, default=0, comment="已批改數")
    average_score = Column(Float, comment="平均分數")
    
    # 題目配置
    question_config = Column(JSON, comment="題目配置（難度分布、知識點等）")
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Assignment(id='{self.id}', title='{self.title}', subject='{self.subject}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "subject": self.subject,
            "grade": self.grade,
            "chapter": self.chapter,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "time_limit": self.time_limit,
            "question_count": self.question_count,
            "difficulty": self.difficulty,
            "shuffle_questions": self.shuffle_questions,
            "shuffle_options": self.shuffle_options,
            "teacher_id": str(self.teacher_id),
            "class_ids": self.class_ids or [],
            "status": self.status,
            "total_students": self.total_students,
            "submitted_count": self.submitted_count,
            "graded_count": self.graded_count,
            "average_score": self.average_score,
            "question_config": self.question_config,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AssignmentSubmission(Base):
    """作業提交模型"""
    __tablename__ = "assignment_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, nullable=False, comment="學生ID")
    
    # 提交資訊
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_spent = Column(Integer, comment="作答時間（秒）")
    score = Column(Float, comment="得分")
    is_graded = Column(Boolean, default=False, comment="是否已批改")
    graded_at = Column(DateTime, comment="批改時間")
    grader_id = Column(Integer, comment="批改教師ID")
    
    # 答案和批改
    answers = Column(JSON, comment="學生答案")
    grading_result = Column(JSON, comment="批改結果")
    feedback = Column(Text, comment="教師反饋")
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AssignmentSubmission(id='{self.id}', assignment_id='{self.assignment_id}', student_id='{self.student_id}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "assignment_id": str(self.assignment_id),
            "student_id": str(self.student_id),
            "submitted_at": self.submitted_at.isoformat(),
            "time_spent": self.time_spent,
            "score": self.score,
            "is_graded": self.is_graded,
            "graded_at": self.graded_at.isoformat() if self.graded_at else None,
            "grader_id": str(self.grader_id) if self.grader_id else None,
            "answers": self.answers,
            "grading_result": self.grading_result,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

