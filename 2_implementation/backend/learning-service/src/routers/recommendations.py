"""
學習推薦 API 路由

提供個人化學習建議和推薦功能
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import LearningRecommendation, WeaknessAnalysis
from ..services.ai_analysis_client import AIAnalysisClient
from ..utils.database import get_db_session
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
ai_client = AIAnalysisClient()


@router.get("/learning", response_model=List[LearningRecommendation])
async def get_learning_recommendations(
    subject: Optional[str] = Query(None, description="科目篩選"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取個人化學習建議"""
    
    try:
        # 獲取用戶最近的學習表現
        recent_performance = await _get_recent_performance(
            current_user.user_id, 
            subject, 
            db_session
        )
        
        # 調用 AI 分析服務獲取建議
        recommendations_data = await ai_client.generate_learning_recommendations(
            user_id=current_user.user_id,
            subject=subject or "all",
            recent_performance=recent_performance
        )
        
        # 轉換為回應格式
        recommendations = []
        for rec in recommendations_data.get("recommendations", []):
            recommendations.append(LearningRecommendation(
                type=rec.get("type", "general"),
                title=rec.get("title", ""),
                description=rec.get("description", ""),
                priority=rec.get("priority", "medium"),
                estimated_time=rec.get("estimated_time", 0),
                difficulty=rec.get("difficulty", "normal"),
                knowledge_points=rec.get("knowledge_points", [])
            ))
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get learning recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取學習建議失敗"
        )


@router.get("/weaknesses", response_model=WeaknessAnalysis)
async def get_weakness_analysis(
    subject: Optional[str] = Query(None, description="科目篩選"),
    time_range: str = Query("30d", description="時間範圍"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取弱點分析"""
    
    try:
        # 獲取用戶學習數據
        learning_data = await _get_learning_data_for_analysis(
            current_user.user_id,
            subject,
            time_range,
            db_session
        )
        
        # 調用 AI 分析服務
        analysis_result = await ai_client.analyze_weaknesses(learning_data)
        
        return WeaknessAnalysis(
            weak_concepts=analysis_result.get("weak_concepts", []),
            knowledge_points_to_strengthen=analysis_result.get("knowledge_points_to_strengthen", []),
            recommendations=analysis_result.get("recommendations", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get weakness analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取弱點分析失敗"
        )


@router.get("/practice-suggestions")
async def get_practice_suggestions(
    subject: str = Query(..., description="科目"),
    difficulty: Optional[str] = Query(None, description="難度等級"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取練習建議"""
    
    try:
        # 獲取用戶在該科目的表現
        performance = await _get_subject_performance(
            current_user.user_id,
            subject,
            db_session
        )
        
        # 根據表現生成練習建議
        suggestions = await _generate_practice_suggestions(
            subject,
            performance,
            difficulty
        )
        
        return {
            "subject": subject,
            "user_performance": performance,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Failed to get practice suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取練習建議失敗"
        )


async def _get_recent_performance(
    user_id: str, 
    subject: Optional[str], 
    db_session: AsyncSession
) -> dict:
    """獲取用戶最近的學習表現"""
    
    from ..models.learning_session import LearningSession
    from sqlalchemy import select, and_, desc
    from datetime import datetime, timedelta
    
    # 查詢最近30天的會話
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    conditions = [
        LearningSession.user_id == user_id,
        LearningSession.created_at >= start_date,
        LearningSession.created_at <= end_date,
        LearningSession.status == "completed"
    ]
    
    if subject:
        conditions.append(LearningSession.subject == subject)
    
    result = await db_session.execute(
        select(LearningSession).where(and_(*conditions)).order_by(desc(LearningSession.created_at))
    )
    sessions = result.scalars().all()
    
    # 計算表現指標
    total_sessions = len(sessions)
    total_questions = sum(s.question_count for s in sessions)
    total_time = sum(s.time_spent or 0 for s in sessions)
    
    # 計算平均分數
    scores = [float(s.overall_score) for s in sessions if s.overall_score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    
    # 按科目分組
    subject_performance = {}
    for session in sessions:
        subj = session.subject
        if subj not in subject_performance:
            subject_performance[subj] = {
                "sessions": 0,
                "questions": 0,
                "time": 0,
                "scores": []
            }
        
        subject_performance[subj]["sessions"] += 1
        subject_performance[subj]["questions"] += session.question_count
        subject_performance[subj]["time"] += session.time_spent or 0
        
        if session.overall_score is not None:
            subject_performance[subj]["scores"].append(float(session.overall_score))
    
    # 計算各科目平均分數
    for subj in subject_performance:
        scores = subject_performance[subj]["scores"]
        subject_performance[subj]["average_score"] = sum(scores) / len(scores) if scores else 0
        del subject_performance[subj]["scores"]
    
    return {
        "total_sessions": total_sessions,
        "total_questions": total_questions,
        "total_time_minutes": total_time,
        "average_score": round(average_score, 2),
        "subject_performance": subject_performance
    }


async def _get_learning_data_for_analysis(
    user_id: str,
    subject: Optional[str],
    time_range: str,
    db_session: AsyncSession
) -> dict:
    """獲取用於分析的學習數據"""
    
    from ..models.learning_session import LearningSession, LearningRecord
    from sqlalchemy import select, and_, desc
    from datetime import datetime, timedelta
    
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
    
    # 查詢會話
    conditions = [
        LearningSession.user_id == user_id,
        LearningSession.created_at >= start_date,
        LearningSession.created_at <= end_date,
        LearningSession.status == "completed"
    ]
    
    if subject:
        conditions.append(LearningSession.subject == subject)
    
    result = await db_session.execute(
        select(LearningSession).where(and_(*conditions))
    )
    sessions = result.scalars().all()
    
    # 獲取學習記錄
    session_ids = [str(s.id) for s in sessions]
    records = []
    
    if session_ids:
        records_result = await db_session.execute(
            select(LearningRecord).where(LearningRecord.session_id.in_(session_ids))
        )
        records = records_result.scalars().all()
    
    # 構建分析數據
    analysis_data = {
        "user_id": user_id,
        "time_range": time_range,
        "sessions": [
            {
                "session_id": str(s.id),
                "subject": s.subject,
                "grade": s.grade,
                "overall_score": float(s.overall_score) if s.overall_score else 0,
                "time_spent": s.time_spent or 0
            }
            for s in sessions
        ],
        "records": [
            {
                "question_id": r.question_id,
                "topic": r.topic,
                "knowledge_points": r.knowledge_points,
                "difficulty": r.difficulty,
                "is_correct": r.is_correct,
                "time_spent": r.time_spent
            }
            for r in records
        ]
    }
    
    return analysis_data


async def _get_subject_performance(
    user_id: str,
    subject: str,
    db_session: AsyncSession
) -> dict:
    """獲取用戶在特定科目的表現"""
    
    from ..models.learning_session import LearningSession
    from sqlalchemy import select, and_, desc
    from datetime import datetime, timedelta
    
    # 查詢最近30天的該科目會話
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    result = await db_session.execute(
        select(LearningSession).where(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.subject == subject,
                LearningSession.created_at >= start_date,
                LearningSession.created_at <= end_date,
                LearningSession.status == "completed"
            )
        ).order_by(desc(LearningSession.created_at))
    )
    sessions = result.scalars().all()
    
    # 計算表現指標
    total_sessions = len(sessions)
    total_questions = sum(s.question_count for s in sessions)
    total_time = sum(s.time_spent or 0 for s in sessions)
    
    # 計算平均分數
    scores = [float(s.overall_score) for s in sessions if s.overall_score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    
    # 計算進步趨勢
    trend = "stable"
    if len(scores) >= 2:
        recent_scores = scores[:3]  # 最近3次
        older_scores = scores[-3:] if len(scores) > 3 else scores
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 5:
            trend = "improving"
        elif recent_avg < older_avg - 5:
            trend = "declining"
    
    return {
        "subject": subject,
        "total_sessions": total_sessions,
        "total_questions": total_questions,
        "total_time_minutes": total_time,
        "average_score": round(average_score, 2),
        "trend": trend,
        "recent_scores": scores[:5]  # 最近5次分數
    }


async def _generate_practice_suggestions(
    subject: str,
    performance: dict,
    difficulty: Optional[str]
) -> list:
    """生成練習建議"""
    
    suggestions = []
    average_score = performance.get("average_score", 0)
    trend = performance.get("trend", "stable")
    
    # 根據分數和趨勢生成建議
    if average_score < 60:
        suggestions.append({
            "type": "foundation",
            "title": "基礎概念練習",
            "description": "建議從基礎概念開始，多做基礎練習題",
            "difficulty": "easy",
            "estimated_time": 30,
            "priority": "high"
        })
    elif average_score < 80:
        suggestions.append({
            "type": "intermediate",
            "title": "進階練習",
            "description": "可以嘗試一些中等難度的題目",
            "difficulty": "normal",
            "estimated_time": 45,
            "priority": "medium"
        })
    else:
        suggestions.append({
            "type": "advanced",
            "title": "挑戰練習",
            "description": "可以嘗試高難度題目來提升能力",
            "difficulty": "hard",
            "estimated_time": 60,
            "priority": "low"
        })
    
    # 根據趨勢調整建議
    if trend == "declining":
        suggestions.append({
            "type": "review",
            "title": "重點複習",
            "description": "建議複習最近學習的重點內容",
            "difficulty": "normal",
            "estimated_time": 40,
            "priority": "high"
        })
    
    # 如果指定了難度，過濾建議
    if difficulty:
        suggestions = [s for s in suggestions if s["difficulty"] == difficulty]
    
    return suggestions 