"""
AI Analysis Service Main Application (Simplified Version)

This is a simplified version for testing purposes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

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

@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    logger.info("🚀 Starting AI Analysis Service (Simplified)...")
    logger.info("✅ AI Analysis Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件"""
    logger.info("🔄 Shutting down AI Analysis Service...")

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "AI Analysis Service is running (Simplified)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "service": "ai-analysis-service",
        "version": "1.0.0",
        "mode": "simplified",
        "databases": {
            "postgresql": "not_configured",
            "redis": "not_configured"
        }
    }

@app.get("/api/v1/weakness-analysis/test")
async def test_weakness_analysis():
    """測試弱點分析端點"""
    return {
        "message": "Weakness analysis endpoint is available",
        "status": "working",
        "note": "This is a simplified version for testing"
    }

@app.get("/api/v1/recommendations/test")
async def test_recommendations():
    """測試學習建議端點"""
    return {
        "message": "Learning recommendations endpoint is available",
        "status": "working",
        "note": "This is a simplified version for testing"
    }

@app.get("/api/v1/trend-analysis/test")
async def test_trend_analysis():
    """測試趨勢分析端點"""
    return {
        "message": "Trend analysis endpoint is available",
        "status": "working",
        "note": "This is a simplified version for testing"
    }

@app.get("/api/v1/vector-search/test")
async def test_vector_search():
    """測試向量搜尋端點"""
    return {
        "message": "Vector search endpoint is available",
        "status": "working",
        "note": "This is a simplified version for testing"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局異常處理"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "internal_error",
                "details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 