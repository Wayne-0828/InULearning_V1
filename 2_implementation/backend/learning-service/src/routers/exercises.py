"""
練習 API 路由

提供練習會話創建、答案提交等 API 端點
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import (
    ExerciseParams, Answer, SubmissionResult, 
    ExerciseResponse, SessionStatus,
    CompleteExerciseRequest, CompleteExerciseResponse
)
from ..services.exercise_service import ExerciseService
from ..utils.database import get_db_session
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exercises", tags=["exercises"])
exercise_service = ExerciseService()


@router.post("/create", response_model=ExerciseResponse)
async def create_exercise(
    params: ExerciseParams,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """創建個人化練習會話"""
    
    try:
        logger.info(f"Creating exercise for user {current_user.user_id}")
        
        result = await exercise_service.create_personalized_exercise(
            user_id=current_user.user_id,
            params=params,
            db_session=db_session
        )
        
        return ExerciseResponse(
            session_id=result["session_id"],
            questions=result["questions"],
            estimated_time=result["estimated_time"],
            created_at=result["created_at"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid exercise parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create exercise: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建練習會話失敗"
        )


@router.post("/{session_id}/submit", response_model=SubmissionResult)
async def submit_answers(
    session_id: str,
    answers: List[Answer],
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """提交答案並獲得批改結果"""
    
    try:
        logger.info(f"Submitting answers for session {session_id}")
        
        result = await exercise_service.submit_answers(
            session_id=session_id,
            answers=answers,
            db_session=db_session
        )
        
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to submit answers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="提交答案失敗"
        )


@router.get("/{session_id}/status", response_model=SessionStatus)
async def get_session_status(
    session_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取會話狀態"""
    
    try:
        from ..models.learning_session import LearningSession
        from sqlalchemy import select
        
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
        
        return SessionStatus(
            session_id=str(session.id),
            status=session.status,
            start_time=session.start_time,
            end_time=session.end_time,
            overall_score=session.overall_score,
            time_spent=session.time_spent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取會話狀態失敗"
        )


@router.delete("/{session_id}")
async def cancel_session(
    session_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """取消會話"""
    
    try:
        from ..models.learning_session import LearningSession
        from sqlalchemy import select, update
        
        # 檢查會話是否存在且屬於當前用戶
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
        
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能取消進行中的會話"
            )
        
        # 更新會話狀態
        await db_session.execute(
            update(LearningSession)
            .where(LearningSession.id == session_id)
            .values(status="cancelled")
        )
        await db_session.commit()
        
        return {"message": "會話已取消"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消會話失敗"
        )


@router.post("/complete", response_model=CompleteExerciseResponse)
async def complete_exercise(
    request: CompleteExerciseRequest,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """完成練習並提交結果（重定向到新的學習歷程API）"""
    
    try:
        # 重定向到新的學習歷程API
        from ..routers.learning_history import complete_exercise as complete_exercise_impl
        return await complete_exercise_impl(request, current_user, db_session)
        
    except Exception as e:
        logger.error(f"Failed to complete exercise: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="完成練習失敗"
        ) 