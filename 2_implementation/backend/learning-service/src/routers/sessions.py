"""
會話管理 API 路由

提供學習會話查詢、歷史記錄等 API 端點
"""

import logging
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel

from ..models.schemas import SessionList, SessionDetail, LearningHistory
from ..models.learning_session import LearningSession, LearningRecord
from ..utils.database import get_db_session
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Pydantic 模型
class SessionCreateRequest(BaseModel):
    session_type: str
    question_count: int
    subject: str
    grade: Optional[str] = None
    chapter: Optional[str] = None

class SessionCreateResponse(BaseModel):
    id: str
    session_type: str
    question_count: int
    subject: str
    status: str
    created_at: datetime


@router.post("/", response_model=SessionCreateResponse, status_code=201)
async def create_session(
    request: SessionCreateRequest,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """創建新的學習會話"""
    
    try:
        # 創建新的學習會話
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        new_session = LearningSession(
            id=session_id,
            user_id=current_user.user_id,
            session_type=request.session_type,
            subject=request.subject,
            grade=request.grade,
            chapter=request.chapter,
            question_count=request.question_count,
            status="active",
            start_time=now,
            created_at=now,
            updated_at=now
        )
        
        db_session.add(new_session)
        await db_session.commit()
        await db_session.refresh(new_session)
        
        logger.info(f"Created session {session_id} for user {current_user.user_id}")
        
        return SessionCreateResponse(
            id=new_session.id,
            session_type=new_session.session_type,
            question_count=new_session.question_count,
            subject=new_session.subject,
            status=new_session.status,
            created_at=new_session.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建學習會話失敗"
        )


@router.get("/", response_model=List[SessionList])
async def get_user_sessions(
    subject: Optional[str] = Query(None, description="科目篩選"),
    status_filter: Optional[str] = Query(None, description="狀態篩選"),
    limit: int = Query(20, ge=1, le=100, description="每頁數量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取用戶的學習會話列表"""
    
    try:
        # 構建查詢條件
        conditions = [LearningSession.user_id == current_user.user_id]
        
        if subject:
            conditions.append(LearningSession.subject == subject)
        
        if status_filter:
            conditions.append(LearningSession.status == status_filter)
        
        # 查詢會話
        query = (
            select(LearningSession)
            .where(and_(*conditions))
            .order_by(desc(LearningSession.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await db_session.execute(query)
        sessions = result.scalars().all()
        
        # 轉換為回應格式
        session_list = []
        for session in sessions:
            session_list.append(SessionList(
                session_id=str(session.id),
                session_type=session.session_type,
                grade=session.grade,
                subject=session.subject,
                publisher=session.publisher,
                chapter=session.chapter,
                difficulty=session.difficulty,
                question_count=session.question_count,
                status=session.status,
                overall_score=session.overall_score,
                start_time=session.start_time,
                end_time=session.end_time,
                time_spent=session.time_spent,
                created_at=session.created_at
            ))
        
        return session_list
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取會話列表失敗"
        )


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session_detail(
    session_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取會話詳細資訊"""
    
    try:
        # 查詢會話
        result = await db_session.execute(
            select(LearningSession).where(
                LearningSession.id == session_id,
                LearningSession.user_id == current_user.user_id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="會話不存在"
            )
        
        # 查詢學習記錄
        records_result = await db_session.execute(
            select(LearningRecord).where(LearningRecord.session_id == session_id)
        )
        records = records_result.scalars().all()
        
        # 轉換為回應格式
        learning_records = []
        for record in records:
            learning_records.append(LearningHistory(
                question_id=record.question_id,
                topic=record.topic,
                knowledge_points=record.knowledge_points,
                difficulty=record.difficulty,
                user_answer=record.user_answer,
                correct_answer=record.correct_answer,
                is_correct=record.is_correct,
                score=record.score,
                time_spent=record.time_spent
            ))
        
        return SessionDetail(
            session_id=str(session.id),
            session_type=session.session_type,
            grade=session.grade,
            subject=session.subject,
            publisher=session.publisher,
            chapter=session.chapter,
            difficulty=session.difficulty,
            question_count=session.question_count,
            status=session.status,
            overall_score=session.overall_score,
            start_time=session.start_time,
            end_time=session.end_time,
            time_spent=session.time_spent,
            created_at=session.created_at,
            learning_records=learning_records
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取會話詳情失敗"
        )


@router.get("/statistics/summary")
async def get_session_statistics(
    time_range: str = Query("30d", description="時間範圍 (7d, 30d, 90d)"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取會話統計摘要"""
    
    try:
        # 計算時間範圍
        end_date = datetime.utcnow()
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # 查詢統計數據
        result = await db_session.execute(
            select(LearningSession).where(
                and_(
                    LearningSession.user_id == current_user.user_id,
                    LearningSession.created_at >= start_date,
                    LearningSession.created_at <= end_date
                )
            )
        )
        sessions = result.scalars().all()
        
        # 計算統計數據
        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.status == "completed")
        total_questions = sum(s.question_count for s in sessions)
        total_time = sum(s.time_spent or 0 for s in sessions)
        
        # 計算平均分數
        completed_with_score = [s for s in sessions if s.overall_score is not None]
        average_score = 0
        if completed_with_score:
            average_score = sum(float(s.overall_score) for s in completed_with_score) / len(completed_with_score)
        
        # 按科目統計
        subject_stats = {}
        for session in sessions:
            subject = session.subject
            if subject not in subject_stats:
                subject_stats[subject] = {
                    "sessions": 0,
                    "questions": 0,
                    "time": 0,
                    "scores": []
                }
            
            subject_stats[subject]["sessions"] += 1
            subject_stats[subject]["questions"] += session.question_count
            subject_stats[subject]["time"] += session.time_spent or 0
            
            if session.overall_score is not None:
                subject_stats[subject]["scores"].append(float(session.overall_score))
        
        # 計算各科目平均分數
        for subject in subject_stats:
            scores = subject_stats[subject]["scores"]
            subject_stats[subject]["average_score"] = sum(scores) / len(scores) if scores else 0
            del subject_stats[subject]["scores"]  # 移除原始分數列表
        
        return {
            "time_range": time_range,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "total_questions": total_questions,
            "total_time_minutes": total_time,
            "average_score": round(average_score, 2),
            "subject_statistics": subject_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get session statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取統計數據失敗"
        ) 