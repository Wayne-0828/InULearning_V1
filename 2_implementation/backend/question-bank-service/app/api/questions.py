from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.database import DatabaseManager, get_database
from app.schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionSearchCriteria,
    PaginatedResponse, Message, BulkImportResult
)
from app.crud import QuestionCRUD
import json

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    db: DatabaseManager = Depends(get_database)
):
    """創建新題目"""
    try:
        question_id = await QuestionCRUD.create_question(db, question)
        created_question = await QuestionCRUD.get_question_by_id(db, question_id)
        return created_question
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建題目失敗: {str(e)}"
        )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """根據ID獲取題目"""
    question = await QuestionCRUD.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="題目不存在"
        )
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    db: DatabaseManager = Depends(get_database)
):
    """更新題目"""
    # 檢查題目是否存在
    existing_question = await QuestionCRUD.get_question_by_id(db, question_id)
    if not existing_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="題目不存在"
        )
    
    # 更新題目
    success = await QuestionCRUD.update_question(db, question_id, question_update)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新題目失敗"
        )
    
    # 返回更新後的題目
    updated_question = await QuestionCRUD.get_question_by_id(db, question_id)
    return updated_question


@router.delete("/{question_id}", response_model=Message)
async def delete_question(
    question_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """刪除題目"""
    success = await QuestionCRUD.delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="題目不存在或刪除失敗"
        )
    
    return {"message": "題目刪除成功"}


@router.get("/", response_model=PaginatedResponse)
async def search_questions(
    grade: Optional[str] = Query(None, description="年級"),
    subject: Optional[str] = Query(None, description="科目"),
    publisher: Optional[str] = Query(None, description="出版社"),
    chapter: Optional[str] = Query(None, description="章節"),
    topic: Optional[str] = Query(None, description="主題"),
    knowledge_point: Optional[List[str]] = Query(None, description="知識點"),
    difficulty: Optional[str] = Query(None, description="難度"),
    question_type: Optional[str] = Query(None, description="題型"),
    tags: Optional[List[str]] = Query(None, description="標籤"),
    keyword: Optional[str] = Query(None, description="關鍵字"),
    limit: int = Query(20, ge=1, le=100, description="每頁數量"),
    skip: int = Query(0, ge=0, description="跳過數量"),
    db: DatabaseManager = Depends(get_database)
):
    """搜尋題目"""
    try:
        criteria = QuestionSearchCriteria(
            grade=grade,
            subject=subject,
            publisher=publisher,
            chapter=chapter,
            topic=topic,
            knowledge_point=knowledge_point,
            difficulty=difficulty,
            question_type=question_type,
            tags=tags,
            keyword=keyword,
            limit=limit,
            skip=skip
        )
        
        result = await QuestionCRUD.search_questions(db, criteria)
        
        # 計算分頁資訊
        total_pages = (result["total"] + limit - 1) // limit
        current_page = (skip // limit) + 1
        
        return PaginatedResponse(
            items=result["items"],
            total=result["total"],
            page=current_page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜尋題目失敗: {str(e)}"
        )


@router.get("/random/", response_model=List[QuestionResponse])
async def get_random_questions(
    grade: str = Query(..., description="年級"),
    subject: str = Query(..., description="科目"),
    publisher: str = Query(..., description="出版社"),
    count: int = Query(10, ge=1, le=50, description="題目數量"),
    exclude_ids: Optional[List[str]] = Query(None, description="排除的題目ID"),
    db: DatabaseManager = Depends(get_database)
):
    """隨機獲取題目"""
    try:
        questions = await QuestionCRUD.get_random_questions(
            db, grade, subject, publisher, count, exclude_ids
        )
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取隨機題目失敗: {str(e)}"
        )


@router.get("/criteria/", response_model=List[QuestionResponse])
async def get_questions_by_criteria(
    grade: str = Query(..., description="年級"),
    subject: str = Query(..., description="科目"),
    publisher: str = Query(..., description="出版社"),
    chapter: Optional[str] = Query(None, description="章節"),
    difficulty: Optional[str] = Query(None, description="難度"),
    knowledge_points: Optional[List[str]] = Query(None, description="知識點"),
    limit: int = Query(10, ge=1, le=100, description="題目數量"),
    db: DatabaseManager = Depends(get_database)
):
    """根據條件獲取題目"""
    try:
        questions = await QuestionCRUD.get_questions_by_criteria(
            db, grade, subject, publisher, chapter, difficulty, knowledge_points, limit
        )
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"根據條件獲取題目失敗: {str(e)}"
        )


@router.post("/bulk-import/", response_model=BulkImportResult)
async def bulk_import_questions(
    questions_data: List[QuestionCreate],
    db: DatabaseManager = Depends(get_database)
):
    """批量匯入題目"""
    total_imported = 0
    total_failed = 0
    errors = []
    
    for i, question_data in enumerate(questions_data):
        try:
            await QuestionCRUD.create_question(db, question_data)
            total_imported += 1
        except Exception as e:
            total_failed += 1
            errors.append(f"第 {i+1} 題匯入失敗: {str(e)}")
    
    return BulkImportResult(
        total_imported=total_imported,
        total_failed=total_failed,
        errors=errors
    ) 