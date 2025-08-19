from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api import auth, users, relationships
from app.database import engine, init_database, check_database_connection
from app.models import Base

# 應用程式生命週期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時初始化
    print("🚀 正在啟動 Auth Service...")
    try:
        init_database()
        print("✅ Auth Service 啟動完成")
    except Exception as e:
        print(f"⚠️ 資料庫初始化失敗，但服務將繼續運行: {e}")
        print("✅ Auth Service 啟動完成 (without database)")
    
    yield
    
    # 關閉時清理
    print("🔄 正在關閉 Auth Service...")
    print("✅ Auth Service 已關閉")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="InULearning Authentication and User Management Service",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
# 註解掉 CORS 中間件，由 Nginx 統一處理 CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(relationships.router, prefix="/api/v1/relationships")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "InULearning Auth Service",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "healthy" if check_database_connection() else "unhealthy"
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": settings.app_version,
        "database": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 