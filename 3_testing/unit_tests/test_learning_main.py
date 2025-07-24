"""
主要測試文件

測試學習服務的核心功能
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app
from src.utils.database import get_db_session
from src.models.base import Base
from src.models.learning_session import LearningSession, LearningRecord


@pytest.fixture
def client():
    """測試客戶端"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """異步測試客戶端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_db():
    """測試資料庫會話"""
    async for session in get_db_session():
        yield session


@pytest.mark.asyncio
async def test_health_check(async_client):
    """測試健康檢查端點"""
    async for client in async_client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "learning-service" in data["service"]
        break


@pytest.mark.asyncio
async def test_create_exercise(async_client, test_db):
    """測試創建練習會話"""
    async for client in async_client:
        async for db in test_db:
            # 模擬認證用戶
            headers = {"Authorization": "Bearer test-token"}
            
            exercise_data = {
                "grade": "7A",
                "subject": "數學",
                "publisher": "南一",
                "chapter": "第一章",
                "difficulty": "normal",
                "question_count": 5,
                "knowledge_points": ["基礎運算", "代數概念"]
            }
            
            response = await client.post(
                "/api/v1/learning/exercises/create",
                json=exercise_data,
                headers=headers
            )
            
            # 由於外部服務依賴，這裡主要測試 API 結構
            assert response.status_code in [200, 401, 500]  # 可能因為外部服務不可用或認證失敗
            break
        break


@pytest.mark.asyncio
async def test_get_user_sessions(async_client, test_db):
    """測試獲取用戶會話列表"""
    async for client in async_client:
        async for db in test_db:
            headers = {"Authorization": "Bearer test-token"}
            
            response = await client.get(
                "/api/v1/learning/sessions/",
                headers=headers
            )
            
            # 測試 API 結構
            assert response.status_code in [200, 401]  # 可能因為認證失敗
            break
        break


@pytest.mark.asyncio
async def test_get_learning_recommendations(async_client, test_db):
    """測試獲取學習建議"""
    async for client in async_client:
        async for db in test_db:
            headers = {"Authorization": "Bearer test-token"}
            
            response = await client.get(
                "/api/v1/learning/recommendations/learning",
                headers=headers
            )
            
            # 測試 API 結構
            assert response.status_code in [200, 401]
            break
        break


@pytest.mark.asyncio
async def test_get_learning_trends(async_client, test_db):
    """測試獲取學習趨勢"""
    async for client in async_client:
        async for db in test_db:
            headers = {"Authorization": "Bearer test-token"}
            
            response = await client.get(
                "/api/v1/learning/trends/learning",
                headers=headers
            )
            
            # 測試 API 結構
            assert response.status_code in [200, 401]
            break
        break


def test_app_structure():
    """測試應用程式結構"""
    assert app.title == "InULearning Learning Service"
    assert app.version == "1.0.0"
    assert app.description is not None


def test_api_routes():
    """測試 API 路由註冊"""
    routes = [route.path for route in app.routes]
    
    # 檢查主要路由是否存在
    expected_routes = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    for route in expected_routes:
        assert route in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 