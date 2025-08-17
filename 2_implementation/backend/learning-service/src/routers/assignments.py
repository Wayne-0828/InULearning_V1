"""
作業管理 API 路由

提供作業創建、分配、提交等基本功能
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from ..utils.database import get_db_session
from ..utils.auth import get_current_user
from ..models.assignment import Assignment, AssignmentSubmission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assignments", tags=["assignments"])

# Pydantic 模型
class AssignmentBase(BaseModel):
    """作業基礎模型"""
    title: str = Field(..., description="作業標題")
    description: str = Field(..., description="作業描述")
    subject: str = Field(..., description="科目")
    grade: str = Field(..., description="年級")
    chapter: Optional[str] = Field(None, description="章節")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    time_limit: Optional[int] = Field(None, description="限時（分鐘）")
    question_count: int = Field(..., description="題目數量")
    difficulty: str = Field("medium", description="難度")
    shuffle_questions: bool = Field(True, description="題目亂序")
    shuffle_options: bool = Field(True, description="選項亂序")

class AssignmentCreate(AssignmentBase):
    """創建作業模型"""
    class_ids: List[str] = Field(..., description="指派班級ID列表")

class AssignmentResponse(AssignmentBase):
    """作業響應模型"""
    id: str
    teacher_id: str
    created_at: datetime
    status: str
    total_students: int
    submitted_count: int
    graded_count: int
    average_score: Optional[float] = None

class AssignmentList(BaseModel):
    """作業列表響應"""
    items: List[AssignmentResponse]
    total: int
    page: int
    page_size: int

# 真實資料庫模型已創建，不再需要模擬資料

@router.get("/", response_model=AssignmentList)
async def get_assignments(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(10, ge=1, le=100, description="每頁數量"),
    subject: Optional[str] = Query(None, description="科目篩選"),
    grade: Optional[str] = Query(None, description="年級篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取作業列表"""
    try:
        # 構建查詢
        query = select(Assignment)
        
        # 應用篩選
        if subject:
            query = query.where(Assignment.subject == subject)
        if grade:
            query = query.where(Assignment.grade == grade)
        if status:
            query = query.where(Assignment.status == status)
        
        # 獲取總數
        count_query = select(func.count(Assignment.id))
        if subject:
            count_query = count_query.where(Assignment.subject == subject)
        if grade:
            count_query = count_query.where(Assignment.grade == grade)
        if status:
            count_query = count_query.where(Assignment.status == status)
        
        total_result = await db_session.execute(count_query)
        total = total_result.scalar()
        
        # 分頁
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 執行查詢
        result = await db_session.execute(query)
        assignments = result.scalars().all()
        
        # 轉換為響應格式
        assignment_items = []
        for assignment in assignments:
            assignment_dict = assignment.to_dict()
            assignment_items.append(assignment_dict)
        
        return AssignmentList(
            items=assignment_items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to get assignments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取作業列表失敗"
        )

@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment: AssignmentCreate,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """創建新作業"""
    try:
        # 檢查用戶是否為教師
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有教師可以創建作業"
            )
        
        # 創建新作業實例
        new_assignment = Assignment(
            title=assignment.title,
            description=assignment.description,
            subject=assignment.subject,
            grade=assignment.grade,
            chapter=assignment.chapter,
            due_date=assignment.due_date,
            time_limit=assignment.time_limit,
            question_count=assignment.question_count,
            difficulty=assignment.difficulty,
            shuffle_questions=assignment.shuffle_questions,
            shuffle_options=assignment.shuffle_options,
            teacher_id=current_user.user_id,
            class_ids=assignment.class_ids,
            status="active",
            total_students=0,  # 根據班級計算
            submitted_count=0,
            graded_count=0,
            average_score=None,
            question_config={}
        )
        
        # 保存到資料庫
        db_session.add(new_assignment)
        await db_session.commit()
        await db_session.refresh(new_assignment)
        
        return new_assignment.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create assignment: {e}")
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建作業失敗"
        )

@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """獲取特定作業詳情"""
    try:
        # 查詢資料庫
        query = select(Assignment).where(Assignment.id == assignment_id)
        result = await db_session.execute(query)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="作業不存在"
            )
        
        return assignment.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assignment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取作業詳情失敗"
        )

@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_update: AssignmentBase,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """更新作業"""
    try:
        # 查詢資料庫
        query = select(Assignment).where(Assignment.id == assignment_id)
        result = await db_session.execute(query)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="作業不存在"
            )
        
        # 檢查權限
        if current_user.user_id != assignment.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己創建的作業"
            )
        
        # 更新作業
        for key, value in assignment_update.dict().items():
            if hasattr(assignment, key):
                setattr(assignment, key, value)
        
        assignment.updated_at = datetime.utcnow()
        
        # 保存到資料庫
        await db_session.commit()
        await db_session.refresh(assignment)
        
        return assignment.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update assignment: {e}")
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新作業失敗"
        )

@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    current_user = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """刪除作業"""
    try:
        # 查詢資料庫
        query = select(Assignment).where(Assignment.id == assignment_id)
        result = await db_session.execute(query)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="作業不存在"
            )
        
        # 檢查權限
        if current_user.user_id != assignment.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能刪除自己創建的作業"
            )
        
        # 刪除作業
        await db_session.delete(assignment)
        await db_session.commit()
        
        return {"message": "作業刪除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete assignment: {e}")
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除作業失敗"
        )
