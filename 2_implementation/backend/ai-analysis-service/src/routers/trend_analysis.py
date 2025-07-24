"""
Trend Analysis Router

This module contains API routes for learning trend analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.schemas import TrendAnalysisRequest, TrendAnalysisResponse
from ..services.trend_analysis_service import TrendAnalysisService
from ..utils.database import get_db
from ..utils.config import get_settings

router = APIRouter(prefix="/trend-analysis", tags=["Trend Analysis"])


def get_trend_analysis_service(db: Session = Depends(get_db)) -> TrendAnalysisService:
    """獲取趨勢分析服務實例"""
    settings = get_settings()
    return TrendAnalysisService(db, settings.gemini_api_key)


@router.post("/analyze", response_model=TrendAnalysisResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    service: TrendAnalysisService = Depends(get_trend_analysis_service)
):
    """
    分析學習趨勢
    
    根據學生的學習歷史數據分析長期學習趨勢，提供進步洞察和建議。
    """
    try:
        result = service.analyze_trends(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"趨勢分析過程中發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/trends")
async def get_user_trends(
    user_id: str,
    limit: int = 5,
    service: TrendAnalysisService = Depends(get_trend_analysis_service)
):
    """
    獲取用戶趨勢分析歷史
    
    獲取指定用戶的趨勢分析歷史記錄。
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit 參數必須在 1-50 之間"
            )
        
        trends = service.get_user_trends(user_id, limit)
        return {
            "user_id": user_id,
            "trends": trends,
            "total_count": len(trends)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取趨勢歷史時發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/subject/{subject}")
async def get_trends_by_subject(
    user_id: str,
    subject: str,
    service: TrendAnalysisService = Depends(get_trend_analysis_service)
):
    """
    根據科目獲取趨勢分析
    
    獲取指定用戶在特定科目的趨勢分析。
    """
    try:
        trends = service.get_trends_by_subject(user_id, subject)
        return {
            "user_id": user_id,
            "subject": subject,
            "trends": trends,
            "total_count": len(trends)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取科目趨勢時發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/latest")
async def get_latest_trend(
    user_id: str,
    subject: Optional[str] = None,
    service: TrendAnalysisService = Depends(get_trend_analysis_service)
):
    """
    獲取最新趨勢分析
    
    獲取指定用戶的最新趨勢分析結果。
    """
    try:
        trend = service.get_latest_trend(user_id, subject)
        if not trend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到用戶 {user_id} 的趨勢分析結果"
            )
        return trend
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取最新趨勢時發生錯誤: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康檢查
    
    檢查趨勢分析服務的健康狀態。
    """
    return {
        "status": "healthy",
        "service": "trend-analysis",
        "message": "趨勢分析服務運行正常"
    } 