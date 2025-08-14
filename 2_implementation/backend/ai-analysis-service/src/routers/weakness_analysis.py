"""
Weakness Analysis Router

This module contains API routes for learning weakness analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../../../../')
sys.path.insert(0, project_root)

try:
    from gemini_api import student_learning_evaluation
except ImportError:
    # 如果無法導入，提供一個備用實現
    def student_learning_evaluation(question, student_answer, temperature=1.0, max_output_tokens=512):
        return {"學生學習狀況評估": "AI 分析暫時無法使用，請稍後再試。"}

from ..models.schemas import WeaknessAnalysisRequest, WeaknessAnalysisResponse
from ..services.weakness_analysis_service import WeaknessAnalysisService
from ..utils.database import get_db
from ..utils.config import get_settings

router = APIRouter(prefix="/weakness-analysis", tags=["Weakness Analysis"])


def get_weakness_analysis_service(db: Session = Depends(get_db)) -> WeaknessAnalysisService:
    """獲取弱點分析服務實例"""
    settings = get_settings()
    return WeaknessAnalysisService(db, settings.gemini_api_key)


@router.post("/analyze", response_model=WeaknessAnalysisResponse)
async def analyze_weaknesses(
    request: WeaknessAnalysisRequest,
    service: WeaknessAnalysisService = Depends(get_weakness_analysis_service)
):
    """
    分析學習弱點
    
    根據學生的答題記錄分析學習弱點，提供詳細的分析報告和改進建議。
    """
    try:
        result = service.analyze_weaknesses(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析過程中發生錯誤: {str(e)}"
        )


@router.post("/question-analysis")
async def analyze_single_question(
    question: dict,
    student_answer: str,
    temperature: float = 1.0,
    max_output_tokens: int = 512
):
    """
    單題 AI 弱點分析
    
    根據單一題目和學生答案進行 AI 弱點分析。
    """
    try:
        # 使用 Gemini API 進行分析
        analysis_result = student_learning_evaluation(
            question=question,
            student_answer=student_answer,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        
        return {
            "success": True,
            "data": analysis_result,
            "message": "AI 弱點分析完成"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 弱點分析失敗: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=WeaknessAnalysisResponse)
async def get_analysis_by_session(
    session_id: str,
    service: WeaknessAnalysisService = Depends(get_weakness_analysis_service)
):
    """
    根據會話ID獲取分析結果
    
    獲取指定學習會話的弱點分析結果。
    """
    try:
        result = service.get_analysis_by_session(session_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到會話 {session_id} 的分析結果"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取分析結果時發生錯誤: {str(e)}"
        )


@router.get("/user/{user_id}/history")
async def get_user_analysis_history(
    user_id: str,
    limit: int = 10,
    service: WeaknessAnalysisService = Depends(get_weakness_analysis_service)
):
    """
    獲取用戶分析歷史
    
    獲取指定用戶的弱點分析歷史記錄。
    """
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit 參數必須在 1-100 之間"
            )
        
        history = service.get_user_analysis_history(user_id, limit)
        return {
            "user_id": user_id,
            "history": history,
            "total_count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取分析歷史時發生錯誤: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康檢查
    
    檢查弱點分析服務的健康狀態。
    """
    return {
        "status": "healthy",
        "service": "weakness-analysis",
        "message": "弱點分析服務運行正常"
    } 