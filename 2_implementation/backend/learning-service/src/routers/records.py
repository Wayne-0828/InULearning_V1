"""
學習記錄查詢路由
提供家長和教師查詢學習記錄的API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..utils.auth import get_current_user
from ..services.auth_service_client import auth_service_client

logger = logging.getLogger(__name__)

router = APIRouter()

def get_token_from_request(request: Request) -> str:
    """從請求中提取JWT token"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    return authorization.split(" ")[1]

@router.get("/parent/children")
async def get_children_learning_records(
    request: Request,
    subject: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """家長查詢子女的學習記錄"""
    
    # 檢查權限
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="只有家長可以查詢子女學習記錄")
    
    try:
        # 獲取JWT token
        token = get_token_from_request(request)
        
        # 獲取家長的子女ID列表
        children_ids = await auth_service_client.get_parent_children_ids(current_user.id, token)
        
        # 返回模擬數據
        return {
            "records": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "message": f"找到 {len(children_ids)} 個子女，但暫無學習記錄"
        }
        
    except Exception as e:
        logger.error(f"查詢子女學習記錄失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="查詢學習記錄失敗")

@router.get("/teacher/students")
async def get_students_learning_records(
    request: Request,
    subject: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """教師查詢學生的學習記錄"""
    
    # 檢查權限
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教師可以查詢學生學習記錄")
    
    try:
        # 獲取JWT token
        token = get_token_from_request(request)
        
        # 獲取教師的學生ID列表
        student_ids = await auth_service_client.get_teacher_student_ids(current_user.id, token)
        
        # 返回模擬數據
        return {
            "records": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "message": f"找到 {len(student_ids)} 個學生，但暫無學習記錄"
        }
        
    except Exception as e:
        logger.error(f"查詢學生學習記錄失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="查詢學習記錄失敗")

@router.get("/parent/statistics")
async def get_children_learning_statistics(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user)
):
    """家長查詢子女的學習統計"""
    
    # 檢查權限
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="只有家長可以查詢子女學習統計")
    
    try:
        # 獲取JWT token
        token = get_token_from_request(request)
        
        # 獲取家長的子女ID列表
        children_ids = await auth_service_client.get_parent_children_ids(current_user.id, token)
        
        # 返回模擬統計數據
        return {
            "total_sessions": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy_rate": 0.0,
            "average_score": 0.0,
            "subjects": {},
            "recent_activity": [],
            "message": f"找到 {len(children_ids)} 個子女，但暫無學習數據"
        }
        
    except Exception as e:
        logger.error(f"查詢子女學習統計失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="查詢學習統計失敗") 