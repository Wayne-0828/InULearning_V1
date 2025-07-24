"""
Vector Search Router

This module contains API routes for vector similarity search.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from ..services.vector_service import VectorService
from ..utils.config import get_settings

router = APIRouter(prefix="/vector-search", tags=["Vector Search"])


def get_vector_service() -> VectorService:
    """獲取向量服務實例"""
    settings = get_settings()
    return VectorService(
        milvus_host=settings.milvus_host,
        milvus_port=settings.milvus_port
    )


@router.post("/add-embedding")
async def add_question_embedding(
    question_id: str,
    question_text: str,
    metadata: Dict[str, Any],
    service: VectorService = Depends(get_vector_service)
):
    """
    添加題目嵌入向量
    
    為指定題目生成並存儲嵌入向量。
    """
    try:
        service.add_question_embedding(question_id, question_text, metadata)
        return {
            "status": "success",
            "message": f"成功添加題目 {question_id} 的嵌入向量",
            "question_id": question_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加嵌入向量時發生錯誤: {str(e)}"
        )


@router.post("/search")
async def search_similar_questions(
    query_text: str,
    top_k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None,
    service: VectorService = Depends(get_vector_service)
):
    """
    搜索相似題目
    
    根據查詢文本搜索相似的題目。
    """
    try:
        if top_k < 1 or top_k > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="top_k 參數必須在 1-50 之間"
            )
        
        similar_questions = service.search_similar_questions(
            query_text, top_k, filter_metadata
        )
        
        return {
            "query_text": query_text,
            "top_k": top_k,
            "similar_questions": similar_questions,
            "total_count": len(similar_questions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索相似題目時發生錯誤: {str(e)}"
        )


@router.put("/update-embedding")
async def update_question_embedding(
    question_id: str,
    question_text: str,
    metadata: Dict[str, Any],
    service: VectorService = Depends(get_vector_service)
):
    """
    更新題目嵌入向量
    
    更新指定題目的嵌入向量。
    """
    try:
        service.update_question_embedding(question_id, question_text, metadata)
        return {
            "status": "success",
            "message": f"成功更新題目 {question_id} 的嵌入向量",
            "question_id": question_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新嵌入向量時發生錯誤: {str(e)}"
        )


@router.delete("/delete-embedding/{question_id}")
async def delete_question_embedding(
    question_id: str,
    service: VectorService = Depends(get_vector_service)
):
    """
    刪除題目嵌入向量
    
    刪除指定題目的嵌入向量。
    """
    try:
        service.delete_question_embedding(question_id)
        return {
            "status": "success",
            "message": f"成功刪除題目 {question_id} 的嵌入向量",
            "question_id": question_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除嵌入向量時發生錯誤: {str(e)}"
        )


@router.post("/batch-add")
async def batch_add_embeddings(
    questions: List[Dict[str, Any]],
    service: VectorService = Depends(get_vector_service)
):
    """
    批量添加嵌入向量
    
    批量為多個題目生成並存儲嵌入向量。
    """
    try:
        if len(questions) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="批量添加的題目數量不能超過 1000"
            )
        
        service.batch_add_embeddings(questions)
        return {
            "status": "success",
            "message": f"成功批量添加 {len(questions)} 個題目的嵌入向量",
            "total_count": len(questions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量添加嵌入向量時發生錯誤: {str(e)}"
        )


@router.get("/stats")
async def get_collection_stats(
    service: VectorService = Depends(get_vector_service)
):
    """
    獲取集合統計信息
    
    獲取向量集合的統計信息。
    """
    try:
        stats = service.get_collection_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取統計信息時發生錯誤: {str(e)}"
        )


@router.get("/health")
async def health_check(
    service: VectorService = Depends(get_vector_service)
):
    """
    健康檢查
    
    檢查向量搜索服務的健康狀態。
    """
    try:
        stats = service.get_collection_stats()
        return {
            "status": "healthy",
            "service": "vector-search",
            "message": "向量搜索服務運行正常",
            "collection_stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "vector-search",
            "message": f"向量搜索服務異常: {str(e)}"
        } 