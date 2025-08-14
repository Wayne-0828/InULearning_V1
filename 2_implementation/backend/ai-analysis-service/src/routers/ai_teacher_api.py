"""
AI Teacher Router

提供基於 Gemini 的教學輔助端點：
- 題目詳解與教學建議（solution_guidance）
- 學生學習狀況評估（student_learning_evaluation）
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..ai_agents.ai_teacher import (
    solution_guidance as generate_solution_guidance_text,
    student_learning_evaluation as generate_student_learning_evaluation_text,
)


router = APIRouter(prefix="/ai-teacher", tags=["ai-teacher"])


class AITeacherRequest(BaseModel):
    question: Dict[str, Any]
    student_answer: str
    temperature: Optional[float] = 1.0
    max_output_tokens: Optional[int] = 512


class AITeacherResponse(BaseModel):
    text: str
    model: str = "gemini-2.0-flash"


@router.post("/solution-guidance", response_model=AITeacherResponse)
async def solution_guidance(request: AITeacherRequest) -> AITeacherResponse:
    """生成「題目詳解與教學建議」文字。"""
    try:
        text = generate_solution_guidance_text(
            question=request.question,
            student_answer=request.student_answer,
            temperature=float(request.temperature or 1.0),
            max_output_tokens=int(request.max_output_tokens or 512),
        )
        return AITeacherResponse(text=text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成題目詳解與教學建議失敗: {str(e)}",
        )


@router.post("/student-learning-evaluation", response_model=AITeacherResponse)
async def student_learning_evaluation(request: AITeacherRequest) -> AITeacherResponse:
    """生成「學生學習狀況評估」文字。"""
    try:
        text = generate_student_learning_evaluation_text(
            question=request.question,
            student_answer=request.student_answer,
            temperature=float(request.temperature or 1.0),
            max_output_tokens=int(request.max_output_tokens or 512),
        )
        return AITeacherResponse(text=text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成學生學習狀況評估失敗: {str(e)}",
        )


