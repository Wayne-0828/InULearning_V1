"""
學習歷程 API 路由

提供練習結果提交和學習歷程查詢的 API 端點
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
import math

from ..models.schemas import (
    CompleteExerciseRequest, CompleteExerciseResponse,
    LearningHistoryQuery, LearningHistoryResponse, LearningSessionSummary,
    LearningStatistics, SessionDetailResponse
)
from ..models.learning_session import LearningSession
from ..models.exercise_record import ExerciseRecord
from ..models.user_learning_profile import UserLearningProfile
from ..utils.database import get_db_session
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["learning_history"])


@router.post("/exercises/complete", response_model=CompleteExerciseResponse)
async def complete_exercise(
    request: CompleteExerciseRequest,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """完成練習並提交結果"""
    
    try:
        logger.info(f"Completing exercise for user {current_user.user_id}")
        
        # 計算統計數據
        total_questions = len(request.exercise_results)
        correct_count = sum(1 for result in request.exercise_results if result.is_correct)
        total_score = sum(result.score for result in request.exercise_results) / total_questions if total_questions > 0 else 0
        accuracy_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # 規範化出版社（若前端未正確帶入，嘗試從多處來源回填）
        def normalize_publisher(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            value = str(value).strip()
            mapping = {
                "南一": "南一",
                "翰林": "翰林",
                "康軒": "康軒",
                # 常見別名/拼寫
                "康轩": "康軒",
                "翰林版": "翰林",
                "南一版": "南一",
                "康軒版": "康軒",
            }
            return mapping.get(value, value)

        derived_publisher: Optional[str] = normalize_publisher(request.publisher)

        # 從 session_metadata.original_session_data 嘗試補值
        try:
            original = (request.session_metadata or {}).get("original_session_data") or {}
            if not derived_publisher:
                derived_publisher = normalize_publisher(original.get("publisher") or original.get("edition"))
        except Exception:
            pass

        # 從第一筆題目結果嘗試補值
        if not derived_publisher and request.exercise_results:
            derived_publisher = normalize_publisher(request.exercise_results[0].publisher)

        # 防守性：限制在允許清單內
        allowed_publishers = {"南一", "翰林", "康軒"}
        if derived_publisher not in allowed_publishers:
            # 最終保底
            derived_publisher = "南一"

        # 創建學習會話
        session = LearningSession(
            user_id=int(current_user.user_id),
            session_name=request.session_name,
            subject=request.subject,
            grade=request.grade,
            chapter=request.chapter,
            publisher=derived_publisher,
            difficulty=request.difficulty,
            knowledge_points=request.knowledge_points,
            question_count=total_questions,
            correct_count=correct_count,
            total_score=total_score,
            accuracy_rate=accuracy_rate,
            time_spent=request.total_time_spent,
            status='completed',
            session_metadata=request.session_metadata,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        db_session.add(session)
        await db_session.flush()  # 獲取 session.id
        
        # 創建練習記錄
        exercise_records = []
        for result in request.exercise_results:
            record_publisher = normalize_publisher(result.publisher) or derived_publisher
            record = ExerciseRecord(
                session_id=session.id,
                user_id=int(current_user.user_id),
                question_id=result.question_id,
                subject=result.subject,
                grade=result.grade,
                chapter=result.chapter,
                publisher=record_publisher,
                knowledge_points=result.knowledge_points,
                question_content=result.question_content,
                answer_choices=result.answer_choices,
                difficulty=result.difficulty,
                question_topic=result.question_topic,
                user_answer=result.user_answer,
                correct_answer=result.correct_answer,
                is_correct=result.is_correct,
                score=result.score,
                explanation=result.explanation,
                time_spent=result.time_spent
            )
            exercise_records.append(record)
        
        db_session.add_all(exercise_records)
        
        # 更新或創建用戶學習檔案
        user_id_int = int(current_user.user_id)
        result = await db_session.execute(
            select(UserLearningProfile).where(UserLearningProfile.user_id == user_id_int)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # 創建新的學習檔案
            profile = UserLearningProfile(
                user_id=user_id_int,
                current_grade=request.grade,
                preferred_subjects=[request.subject],
                preferred_publishers=[request.publisher],
                total_practice_time=request.total_time_spent or 0,
                total_sessions=1,
                total_questions=total_questions,
                correct_questions=correct_count,
                overall_accuracy=accuracy_rate,
                last_practice_date=datetime.utcnow().date()
            )
            db_session.add(profile)
        else:
            # 更新現有檔案
            profile.total_practice_time += request.total_time_spent or 0
            profile.total_sessions += 1
            profile.total_questions += total_questions
            profile.correct_questions += correct_count
            profile.overall_accuracy = (profile.correct_questions / profile.total_questions * 100) if profile.total_questions > 0 else 0
            profile.last_practice_date = datetime.utcnow().date()
            
            # 更新偏好科目和出版社
            if request.subject not in (profile.preferred_subjects or []):
                profile.preferred_subjects = (profile.preferred_subjects or []) + [request.subject]
            if request.publisher not in (profile.preferred_publishers or []):
                profile.preferred_publishers = (profile.preferred_publishers or []) + [request.publisher]
        
        await db_session.commit()
        
        return CompleteExerciseResponse(
            session_id=str(session.id),
            total_questions=total_questions,
            correct_count=correct_count,
            total_score=total_score,
            accuracy_rate=accuracy_rate,
            time_spent=request.total_time_spent or 0,
            created_at=session.created_at
        )
        
    except Exception as e:
        await db_session.rollback()
        logger.error(f"Failed to complete exercise: {e}", exc_info=True)
        
        # 根據錯誤類型返回更具體的錯誤信息
        if "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="練習結果已存在，請勿重複提交"
            )
        elif "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="數據關聯錯誤，請檢查提交的數據"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"提交練習結果失敗: {str(e)[:100]}"
            )


@router.get("/recent", response_model=LearningHistoryResponse)
async def get_recent_learning_records(
    limit: int = Query(5, ge=1, le=20, description="記錄數量"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取最近的學習記錄"""
    
    try:
        logger.info(f"Getting recent {limit} learning records for user {current_user.user_id}")
        
        user_id_int = int(current_user.user_id)
        
        # 查詢最近的學習記錄
        result = await db_session.execute(
            select(LearningSession)
            .where(LearningSession.user_id == user_id_int)
            .order_by(desc(LearningSession.start_time))
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        # 轉換為響應格式
        session_summaries = []
        for session in sessions:
            summary = LearningSessionSummary(
                session_id=str(session.id),
                session_name=session.session_name,
                subject=session.subject,
                grade=session.grade,
                chapter=session.chapter,
                publisher=session.publisher,
                difficulty=session.difficulty,
                knowledge_points=session.knowledge_points or [],
                question_count=session.question_count,
                correct_count=session.correct_count,
                total_score=float(session.total_score) if session.total_score else 0.0,
                accuracy_rate=float(session.accuracy_rate) if session.accuracy_rate else 0.0,
                time_spent=session.time_spent,
                status=session.status,
                start_time=session.start_time,
                end_time=session.end_time
            )
            session_summaries.append(summary)
        
        return LearningHistoryResponse(
            sessions=session_summaries,
            total=len(session_summaries),
            page=1,
            page_size=limit,
            total_pages=1
        )
        
    except Exception as e:
        logger.error(f"Failed to get recent learning records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查詢最近學習記錄失敗"
        )


@router.get("/records", response_model=LearningHistoryResponse)
async def get_learning_records(
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選"),
    publisher: Optional[str] = Query(None, description="出版社篩選"),
    start_date: Optional[datetime] = Query(None, description="開始日期"),
    end_date: Optional[datetime] = Query(None, description="結束日期"),
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(20, ge=1, le=100, description="每頁數量"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """查詢學習歷程記錄"""
    
    try:
        logger.info(f"Getting learning records for user {current_user.user_id}")

        # 規範化時間參數（將含有時區資訊的時間轉為 UTC 並移除 tzinfo）
        try:
            if start_date and getattr(start_date, 'tzinfo', None) is not None:
                start_date = start_date.astimezone(timezone.utc).replace(tzinfo=None)
            if end_date and getattr(end_date, 'tzinfo', None) is not None:
                end_date = end_date.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception as dt_err:
            logger.warning(f"Datetime normalization failed: {dt_err}")
        
        # 構建查詢條件
        user_id_int = int(current_user.user_id)
        conditions = [LearningSession.user_id == user_id_int]
        
        if subject:
            conditions.append(LearningSession.subject == subject)
        if grade:
            conditions.append(LearningSession.grade == grade)
        if publisher:
            conditions.append(LearningSession.publisher == publisher)
        if start_date:
            conditions.append(LearningSession.start_time >= start_date)
        if end_date:
            conditions.append(LearningSession.start_time <= end_date)
        
        # 查詢總數
        count_result = await db_session.execute(
            select(func.count(LearningSession.id)).where(and_(*conditions))
        )
        total = count_result.scalar()
        
        # 分頁查詢
        offset = (page - 1) * page_size
        result = await db_session.execute(
            select(LearningSession)
            .where(and_(*conditions))
            .order_by(desc(LearningSession.start_time))
            .offset(offset)
            .limit(page_size)
        )
        sessions = result.scalars().all()
        
        # 轉換為響應格式
        session_summaries = []
        for session in sessions:
            summary = LearningSessionSummary(
                session_id=str(session.id),
                session_name=session.session_name,
                subject=session.subject,
                grade=session.grade,
                chapter=session.chapter,
                publisher=session.publisher,
                difficulty=session.difficulty,
                knowledge_points=session.knowledge_points or [],
                question_count=session.question_count,
                correct_count=session.correct_count,
                total_score=float(session.total_score) if session.total_score else 0.0,
                accuracy_rate=float(session.accuracy_rate) if session.accuracy_rate else 0.0,
                time_spent=session.time_spent,
                status=session.status,
                start_time=session.start_time,
                end_time=session.end_time
            )
            session_summaries.append(summary)
        
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return LearningHistoryResponse(
            sessions=session_summaries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Failed to get learning records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查詢學習記錄失敗"
        )


@router.get("/records/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """查詢會話詳細資訊"""
    
    try:
        logger.info(f"Getting session detail for session {session_id}")
        
        # 查詢會話
        result = await db_session.execute(
            select(LearningSession).where(
                and_(
                    LearningSession.id == session_id,
                    LearningSession.user_id == int(current_user.user_id)
                )
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="會話不存在"
            )
        
        # 查詢練習記錄
        records_result = await db_session.execute(
            select(ExerciseRecord)
            .where(ExerciseRecord.session_id == session_id)
            .order_by(ExerciseRecord.created_at)
        )
        exercise_records = records_result.scalars().all()
        
        # 轉換為響應格式
        session_summary = LearningSessionSummary(
            session_id=str(session.id),
            session_name=session.session_name,
            subject=session.subject,
            grade=session.grade,
            chapter=session.chapter,
            publisher=session.publisher,
            difficulty=session.difficulty,
            knowledge_points=session.knowledge_points or [],
            question_count=session.question_count,
            correct_count=session.correct_count,
            total_score=float(session.total_score) if session.total_score else 0.0,
            accuracy_rate=float(session.accuracy_rate) if session.accuracy_rate else 0.0,
            time_spent=session.time_spent,
            status=session.status,
            start_time=session.start_time,
            end_time=session.end_time
        )
        
        exercise_records_data = [record.to_dict() for record in exercise_records]
        
        return SessionDetailResponse(
            session=session_summary,
            exercise_records=exercise_records_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查詢會話詳情失敗"
        )


@router.get("/statistics", response_model=LearningStatistics)
async def get_learning_statistics(
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取學習統計資訊"""
    
    try:
        logger.info(f"Getting learning statistics for user {current_user.user_id}")
        
        # 查詢用戶學習檔案
        result = await db_session.execute(
            select(UserLearningProfile).where(UserLearningProfile.user_id == int(current_user.user_id))
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            # 返回空統計
            return LearningStatistics(
                total_sessions=0,
                total_questions=0,
                total_correct=0,
                overall_accuracy=0.0,
                total_time_spent=0,
                subject_stats={},
                recent_performance=[]
            )
        
        # 查詢科目統計
        subject_stats_result = await db_session.execute(
            select(
                LearningSession.subject,
                func.count(LearningSession.id).label('sessions'),
                func.sum(LearningSession.question_count).label('questions'),
                func.sum(LearningSession.correct_count).label('correct'),
                func.avg(LearningSession.accuracy_rate).label('avg_accuracy'),
                func.avg(LearningSession.total_score).label('avg_score')
            )
            .where(LearningSession.user_id == int(current_user.user_id))
            .group_by(LearningSession.subject)
        )
        
        subject_stats = {}
        for row in subject_stats_result:
            subject_stats[row.subject] = {
                "sessions": row.sessions,
                "questions": row.questions or 0,
                "correct": row.correct or 0,
                "accuracy": float(row.avg_accuracy) if row.avg_accuracy else 0.0,
                "avg_score": float(row.avg_score) if row.avg_score else 0.0
            }
        
        # 查詢近期表現（最近10次會話）
        recent_result = await db_session.execute(
            select(LearningSession)
            .where(LearningSession.user_id == int(current_user.user_id))
            .order_by(desc(LearningSession.start_time))
            .limit(10)
        )
        recent_sessions = recent_result.scalars().all()
        
        recent_performance = []
        for session in recent_sessions:
            recent_performance.append({
                "session_id": str(session.id),
                "subject": session.subject,
                "date": session.start_time.isoformat(),
                "score": float(session.total_score) if session.total_score else 0.0,
                "accuracy": float(session.accuracy_rate) if session.accuracy_rate else 0.0,
                "questions": session.question_count
            })
        
        return LearningStatistics(
            total_sessions=profile.total_sessions,
            total_questions=profile.total_questions,
            total_correct=profile.correct_questions,
            overall_accuracy=float(profile.overall_accuracy) if profile.overall_accuracy else 0.0,
            total_time_spent=profile.total_practice_time,
            subject_stats=subject_stats,
            recent_performance=recent_performance
        )
        
    except Exception as e:
        logger.error(f"Failed to get learning statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查詢學習統計失敗"
        )