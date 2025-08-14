"""
AI Analysis Service Main Application

This is the main entry point for the AI analysis service.
"""

#1212

import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import (learning_recommendation_router, trend_analysis_router,
                      vector_search_router, weakness_analysis_router)
from .utils.config import get_settings
from .utils.database import (check_postgresql_connection,
                             check_redis_connection, init_db)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="AI Analysis Service",
    description="InULearning AI Analysis Service for learning weakness analysis and recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境中應該限制具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(weakness_analysis_router, prefix="/api/v1")
app.include_router(learning_recommendation_router, prefix="/api/v1")
app.include_router(trend_analysis_router, prefix="/api/v1")
app.include_router(vector_search_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    logger.info("🚀 Starting AI Analysis Service...")
    
    try:
        # 初始化資料庫（可選，不強制）
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization failed (non-critical): {e}")
            logger.info("🔄 Continuing startup without database initialization")
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件"""
    logger.info("🔄 Shutting down AI Analysis Service...")


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "AI Analysis Service is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    try:
        # 檢查資料庫連接
        postgresql_status = check_postgresql_connection()
        redis_status = await check_redis_connection()
        
        overall_status = "healthy" if postgresql_status and redis_status else "unhealthy"
        
        return {
            "status": overall_status,
            "service": "ai-analysis-service",
            "version": "1.0.0",
            "databases": {
                "postgresql": "connected" if postgresql_status else "disconnected",
                "redis": "connected" if redis_status else "disconnected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ai-analysis-service",
            "version": "1.0.0",
            "error": str(e)
        }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域異常處理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "service": "ai-analysis-service"
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 