"""
Learning Recommendation Router

This module contains API routes for learning recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.schemas import LearningRecommendationRequest, LearningRecommendationResponse
from ..services.learning_recommendation_service import LearningRecommendationService
from ..utils.database import get_db
from ..utils.config import get_settings

router = APIRouter(prefix="/learning-recommendation", tags=["Learning Recommendation"])


def get_learning_recommendation_service(db: Session = Depends(get_db)) -> LearningRecommendationService:
    """獲取學習建議服務實例"""
    settings = get_settings()
    return LearningRecommendationService(db, settings.gemini_api_key)


@router.post("/generate", response_model=LearningRecommendationResponse)
async def generate_recommendations(
    request: LearningRecommendationRequest,
    service: LearningRecommendationService = Depends(get_learning_recommendation_service)
):
    """
    生成學習建議
    
    根據學生的弱點和學習需求生成個人化的學習建議和推薦題目。
    """
    try:
        result = service.generate_recommendations(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成建議過程中發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/recommendations")
async def get_user_recommendations(
    user_id: str,
    limit: int = 5,
    service: LearningRecommendationService = Depends(get_learning_recommendation_service)
):
    """
    獲取用戶推薦歷史
    
    獲取指定用戶的學習建議歷史記錄。
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit 參數必須在 1-50 之間"
            )
        
        recommendations = service.get_user_recommendations(user_id, limit)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取推薦歷史時發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/subject/{subject}")
async def get_recommendations_by_subject(
    user_id: str,
    subject: str,
    service: LearningRecommendationService = Depends(get_learning_recommendation_service)
):
    """
    根據科目獲取推薦
    
    獲取指定用戶在特定科目的學習建議。
    """
    try:
        recommendations = service.get_recommendations_by_subject(user_id, subject)
        return {
            "user_id": user_id,
            "subject": subject,
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取科目推薦時發生錯誤: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康檢查
    
    檢查學習建議服務的健康狀態。
    """
    return {
        "status": "healthy",
        "service": "learning-recommendation",
        "message": "學習建議服務運行正常"
    } 