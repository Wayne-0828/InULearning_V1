"""
InULearning Learning Service - 核心學習服務

主要功能：
- 個人化練習會話管理
- 答案提交與自動批改
- 學習歷程追蹤
- AI 弱點分析整合
- 學習趨勢分析

作者: AIPE01_group2
版本: v1.0.0
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routers import exercises, sessions, recommendations, trends, records
from .utils.logging_config import setup_logging
from .utils.auth import get_current_user
from .utils.exceptions import (
    LearningException, 
    QuestionBankException, 
    AIAnalysisException,
    SessionNotFoundException,
    InvalidSessionException
)

# 設置日誌
setup_logging()
logger = logging.getLogger(__name__)

# 應用程式生命週期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時初始化
    logger.info("正在啟動 Learning Service...")
    try:
        from .utils.database import init_database
        await init_database()
        logger.info("Learning Service 啟動完成")
    except Exception as e:
        logger.warning(f"Database initialization failed, but service will continue: {e}")
        logger.info("Learning Service 啟動完成 (without database)")
    
    yield
    
    # 關閉時清理
    logger.info("正在關閉 Learning Service...")
    try:
        from .utils.database import close_database
        await close_database()
    except Exception as e:
        logger.warning(f"Database cleanup failed: {e}")
    logger.info("Learning Service 已關閉")

# 創建 FastAPI 應用
app = FastAPI(
    title="InULearning Learning Service",
    description="個人化學習平台核心學習服務",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 暫時禁用 TrustedHostMiddleware 以解決主機標頭問題
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
# )

# 全局異常處理
@app.exception_handler(LearningException)
async def learning_exception_handler(request, exc: LearningException):
    """學習服務異常處理"""
    logger.error(f"Learning Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(QuestionBankException)
async def question_bank_exception_handler(request, exc: QuestionBankException):
    """題庫服務異常處理"""
    logger.error(f"Question Bank Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(AIAnalysisException)
async def ai_analysis_exception_handler(request, exc: AIAnalysisException):
    """AI 分析服務異常處理"""
    logger.error(f"AI Analysis Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(SessionNotFoundException)
async def session_not_found_handler(request, exc: SessionNotFoundException):
    """會話不存在異常處理"""
    logger.warning(f"Session not found: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(InvalidSessionException)
async def invalid_session_handler(request, exc: InvalidSessionException):
    """無效會話異常處理"""
    logger.warning(f"Invalid session: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """請求驗證異常處理"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "請求參數驗證失敗",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    """HTTP 異常處理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": None
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用異常處理"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "內部伺服器錯誤",
                "details": "請稍後再試"
            }
        }
    )

# 註冊路由
app.include_router(
    exercises.router,
    prefix="/api/v1/learning",
    tags=["練習管理"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    sessions.router,
    prefix="/api/v1/learning",
    tags=["學習會話"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    recommendations.router,
    prefix="/api/v1/learning",
    tags=["學習建議"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    trends.router,
    prefix="/api/v1/learning",
    tags=["學習趨勢"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    records.router,
    prefix="/api/v1/learning",
    tags=["學習記錄"],
    dependencies=[Depends(get_current_user)]
)

# 健康檢查端點
@app.get("/health", tags=["系統"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "learning-service",
        "version": "1.0.0",
        "timestamp": "2024-12-19T10:30:00Z"
    }

# 根端點
@app.get("/", tags=["系統"])
async def root():
    """根端點"""
    return {
        "message": "InULearning Learning Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 