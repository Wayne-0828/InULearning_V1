"""
學習趨勢分析 API 路由

提供學習進度趨勢分析和預測功能
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import LearningTrend, PerformancePrediction
from ..services.ai_analysis_client import AIAnalysisClient
from ..utils.database import get_db_session
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trends", tags=["trends"])
ai_client = AIAnalysisClient()


@router.get("/learning", response_model=LearningTrend)
async def get_learning_trends(
    subject: Optional[str] = Query(None, description="科目篩選"),
    time_range: str = Query("30d", description="時間範圍 (7d, 30d, 90d)"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取學習趨勢分析"""
    
    try:
        # 調用 AI 分析服務
        trends_data = await ai_client.analyze_learning_trends(
            user_id=current_user.user_id,
            subject=subject or "all",
            time_range=time_range
        )
        
        return LearningTrend(
            trend=trends_data.get("trend", "stable"),
            improvement_rate=trends_data.get("improvement_rate", 0.0),
            consistency_score=trends_data.get("consistency_score", 0.0),
            recommendations=trends_data.get("recommendations", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get learning trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取學習趨勢失敗"
        )


@router.get("/performance-prediction", response_model=PerformancePrediction)
async def get_performance_prediction(
    subject: str = Query(..., description="科目"),
    target_exam: str = Query(..., description="目標考試"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取考試表現預測"""
    
    try:
        # 調用 AI 分析服務
        prediction_data = await ai_client.predict_performance(
            user_id=current_user.user_id,
            subject=subject,
            target_exam=target_exam
        )
        
        return PerformancePrediction(
            predicted_score=prediction_data.get("predicted_score", 0.0),
            confidence=prediction_data.get("confidence", 0.0),
            risk_factors=prediction_data.get("risk_factors", []),
            recommendations=prediction_data.get("recommendations", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get performance prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取表現預測失敗"
        )


@router.get("/progress-chart")
async def get_progress_chart(
    subject: Optional[str] = Query(None, description="科目篩選"),
    time_range: str = Query("30d", description="時間範圍"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取學習進度圖表數據"""
    
    try:
        # 獲取學習數據
        chart_data = await _generate_progress_chart_data(
            current_user.user_id,
            subject,
            time_range,
            db_session
        )
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Failed to get progress chart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取進度圖表失敗"
        )


@router.get("/subject-comparison")
async def get_subject_comparison(
    time_range: str = Query("30d", description="時間範圍"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取科目間比較數據"""
    
    try:
        # 獲取各科目表現數據
        comparison_data = await _generate_subject_comparison_data(
            current_user.user_id,
            time_range,
            db_session
        )
        
        return comparison_data
        
    except Exception as e:
        logger.error(f"Failed to get subject comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取科目比較失敗"
        )


@router.get("/weekly-report")
async def get_weekly_report(
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取週學習報告"""
    
    try:
        # 生成週報告數據
        weekly_data = await _generate_weekly_report_data(
            current_user.user_id,
            db_session
        )
        
        return weekly_data
        
    except Exception as e:
        logger.error(f"Failed to get weekly report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取週報告失敗"
        )


async def _generate_progress_chart_data(
    user_id: str,
    subject: Optional[str],
    time_range: str,
    db_session: AsyncSession
) -> dict:
    """生成進度圖表數據"""
    
    from ..models.learning_session import LearningSession
    from sqlalchemy import select, and_, func
    from datetime import datetime, timedelta
    
    # 計算時間範圍
    end_date = datetime.utcnow()
    if time_range == "7d":
        start_date = end_date - timedelta(days=7)
        group_by = func.date(LearningSession.created_at)
    elif time_range == "30d":
        start_date = end_date - timedelta(days=30)
        group_by = func.date(LearningSession.created_at)
    elif time_range == "90d":
        start_date = end_date - timedelta(days=90)
        group_by = func.date_trunc('week', LearningSession.created_at)
    else:
        start_date = end_date - timedelta(days=30)
        group_by = func.date(LearningSession.created_at)
    
    # 構建查詢條件
    conditions = [
        LearningSession.user_id == user_id,
        LearningSession.created_at >= start_date,
        LearningSession.created_at <= end_date,
        LearningSession.status == "completed"
    ]
    
    if subject:
        conditions.append(LearningSession.subject == subject)
    
    # 查詢每日/每週的學習數據
    query = (
        select(
            group_by.label('date'),
            func.count(LearningSession.id).label('sessions'),
            func.sum(LearningSession.question_count).label('questions'),
            func.avg(LearningSession.overall_score).label('avg_score'),
            func.sum(LearningSession.time_spent).label('total_time')
        )
        .where(and_(*conditions))
        .group_by(group_by)
        .order_by(group_by)
    )
    
    result = await db_session.execute(query)
    rows = result.fetchall()
    
    # 構建圖表數據
    chart_data = {
        "labels": [],
        "sessions": [],
        "questions": [],
        "scores": [],
        "time": []
    }
    
    for row in rows:
        chart_data["labels"].append(row.date.strftime("%Y-%m-%d"))
        chart_data["sessions"].append(row.sessions)
        chart_data["questions"].append(row.questions)
        chart_data["scores"].append(round(float(row.avg_score or 0), 2))
        chart_data["time"].append(row.total_time or 0)
    
    return {
        "time_range": time_range,
        "subject": subject or "all",
        "chart_data": chart_data
    }


async def _generate_subject_comparison_data(
    user_id: str,
    time_range: str,
    db_session: AsyncSession
) -> dict:
    """生成科目比較數據"""
    
    from ..models.learning_session import LearningSession
    from sqlalchemy import select, and_, func
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
    
    # 查詢各科目統計數據
    query = (
        select(
            LearningSession.subject,
            func.count(LearningSession.id).label('sessions'),
            func.sum(LearningSession.question_count).label('questions'),
            func.avg(LearningSession.overall_score).label('avg_score'),
            func.sum(LearningSession.time_spent).label('total_time')
        )
        .where(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.created_at >= start_date,
                LearningSession.created_at <= end_date,
                LearningSession.status == "completed"
            )
        )
        .group_by(LearningSession.subject)
    )
    
    result = await db_session.execute(query)
    rows = result.fetchall()
    
    # 構建比較數據
    comparison_data = {
        "subjects": [],
        "sessions": [],
        "questions": [],
        "scores": [],
        "time": []
    }
    
    for row in rows:
        comparison_data["subjects"].append(row.subject)
        comparison_data["sessions"].append(row.sessions)
        comparison_data["questions"].append(row.questions)
        comparison_data["scores"].append(round(float(row.avg_score or 0), 2))
        comparison_data["time"].append(row.total_time or 0)
    
    return {
        "time_range": time_range,
        "comparison_data": comparison_data
    }


async def _generate_weekly_report_data(
    user_id: str,
    db_session: AsyncSession
) -> dict:
    """生成週學習報告數據"""
    
    from ..models.learning_session import LearningSession
    from sqlalchemy import select, and_, func
    from datetime import datetime, timedelta
    
    # 計算本週時間範圍
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # 查詢本週學習數據
    weekly_query = (
        select(
            func.count(LearningSession.id).label('sessions'),
            func.sum(LearningSession.question_count).label('questions'),
            func.avg(LearningSession.overall_score).label('avg_score'),
            func.sum(LearningSession.time_spent).label('total_time')
        )
        .where(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.created_at >= start_date,
                LearningSession.created_at <= end_date,
                LearningSession.status == "completed"
            )
        )
    )
    
    weekly_result = await db_session.execute(weekly_query)
    weekly_data = weekly_result.fetchone()
    
    # 查詢上週數據作為比較
    last_week_start = start_date - timedelta(days=7)
    last_week_query = (
        select(
            func.count(LearningSession.id).label('sessions'),
            func.sum(LearningSession.question_count).label('questions'),
            func.avg(LearningSession.overall_score).label('avg_score'),
            func.sum(LearningSession.time_spent).label('total_time')
        )
        .where(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.created_at >= last_week_start,
                LearningSession.created_at < start_date,
                LearningSession.status == "completed"
            )
        )
    )
    
    last_week_result = await db_session.execute(last_week_query)
    last_week_data = last_week_result.fetchone()
    
    # 計算變化率
    def calculate_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 2)
    
    # 構建週報告
    weekly_report = {
        "period": "本週",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "summary": {
            "sessions": {
                "current": weekly_data.sessions or 0,
                "previous": last_week_data.sessions or 0,
                "change": calculate_change(weekly_data.sessions or 0, last_week_data.sessions or 0)
            },
            "questions": {
                "current": weekly_data.questions or 0,
                "previous": last_week_data.questions or 0,
                "change": calculate_change(weekly_data.questions or 0, last_week_data.questions or 0)
            },
            "avg_score": {
                "current": round(float(weekly_data.avg_score or 0), 2),
                "previous": round(float(last_week_data.avg_score or 0), 2),
                "change": calculate_change(float(weekly_data.avg_score or 0), float(last_week_data.avg_score or 0))
            },
            "total_time": {
                "current": weekly_data.total_time or 0,
                "previous": last_week_data.total_time or 0,
                "change": calculate_change(weekly_data.total_time or 0, last_week_data.total_time or 0)
            }
        },
        "highlights": [],
        "recommendations": []
    }
    
    # 生成亮點
    if weekly_data.sessions and weekly_data.sessions > 0:
        weekly_report["highlights"].append(f"本週完成了 {weekly_data.sessions} 個學習會話")
    
    if weekly_data.questions and weekly_data.questions > 0:
        weekly_report["highlights"].append(f"練習了 {weekly_data.questions} 道題目")
    
    avg_score = float(weekly_data.avg_score or 0)
    if avg_score > 80:
        weekly_report["highlights"].append("平均分數表現優秀！")
    elif avg_score > 60:
        weekly_report["highlights"].append("平均分數表現良好")
    
    # 生成建議
    if weekly_data.sessions and weekly_data.sessions < 3:
        weekly_report["recommendations"].append("建議增加學習頻率，每週至少完成 3 個會話")
    
    if avg_score < 60:
        weekly_report["recommendations"].append("建議加強基礎練習，提升答題準確率")
    
    total_time = weekly_data.total_time or 0
    if total_time < 120:  # 少於2小時
        weekly_report["recommendations"].append("建議增加學習時間，每週至少學習 2 小時")
    
    return weekly_report 