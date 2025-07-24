import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from src.main import app

client = TestClient(app)

class TestAPIIntegration:
    """API 整合測試"""

    @patch('src.routers.weakness_analysis.get_weakness_analysis_service')
    def test_weakness_analysis_api(self, mock_service):
        """測試弱點分析 API"""
        # 模擬服務回應
        mock_service_instance = Mock()
        mock_service_instance.analyze_weaknesses.return_value = {
            "analysis_id": "test-analysis-001",
            "session_id": "test-session-001",
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "weakness_points": [
                {
                    "knowledge_point": "algebra",
                    "difficulty_level": "medium",
                    "error_rate": 0.75,
                    "description": "在解一元一次方程式時經常出錯"
                }
            ],
            "overall_assessment": "需要加強代數運算能力",
            "created_at": "2024-12-20T10:00:00Z"
        }
        mock_service.return_value = mock_service_instance

        # 測試請求資料
        test_data = {
            "session_id": "test-session-001",
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "answer_records": [
                {
                    "question_id": "q001",
                    "user_answer": "A",
                    "correct_answer": "B",
                    "is_correct": False,
                    "time_spent": 45,
                    "knowledge_points": ["algebra", "equations"]
                }
            ]
        }

        response = client.post("/api/v1/weakness-analysis/analyze", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"] == "test-analysis-001"
        assert data["session_id"] == "test-session-001"

    @patch('src.routers.learning_recommendation.get_learning_recommendation_service')
    def test_learning_recommendation_api(self, mock_service):
        """測試學習建議 API"""
        # 模擬服務回應
        mock_service_instance = Mock()
        mock_service_instance.generate_recommendations.return_value = {
            "recommendation_id": "test-rec-001",
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "study_plan": "建議每天練習 30 分鐘代數題目",
            "recommended_questions": [],
            "created_at": "2024-12-20T10:00:00Z"
        }
        mock_service.return_value = mock_service_instance

        # 測試請求資料
        test_data = {
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "weakness_points": [
                {
                    "knowledge_point": "algebra",
                    "difficulty_level": "medium",
                    "error_rate": 0.75,
                    "description": "在解一元一次方程式時經常出錯"
                }
            ],
            "learning_goals": ["提升代數運算能力"]
        }

        response = client.post("/api/v1/learning-recommendation/generate", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_id"] == "test-rec-001"
        assert data["user_id"] == "test-user-001"

    @patch('src.routers.trend_analysis.get_trend_analysis_service')
    def test_trend_analysis_api(self, mock_service):
        """測試趨勢分析 API"""
        # 模擬服務回應
        mock_service_instance = Mock()
        mock_service_instance.analyze_trends.return_value = {
            "analysis_id": "test-trend-001",
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "time_range": "last_30_days",
            "overall_trend": "進步",
            "subject_performance": {
                "algebra": "良好",
                "geometry": "需要加強"
            },
            "recommendations": ["建議增加幾何練習時間"],
            "created_at": "2024-12-20T10:00:00Z"
        }
        mock_service.return_value = mock_service_instance

        # 測試請求資料
        test_data = {
            "user_id": "test-user-001",
            "subject": "mathematics",
            "grade": "grade_7",
            "version": "version_2024",
            "time_range": "last_30_days"
        }

        response = client.post("/api/v1/trend-analysis/analyze", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"] == "test-trend-001"
        assert data["overall_trend"] == "進步"

    @patch('src.routers.vector_search.get_vector_service')
    def test_vector_search_api(self, mock_service):
        """測試向量搜尋 API"""
        # 模擬服務回應
        mock_service_instance = Mock()
        mock_service_instance.add_question_embedding.return_value = True
        mock_service_instance.search_similar_questions.return_value = [
            {
                "question_id": "q001",
                "question_text": "解一元一次方程式 2x + 3 = 7",
                "metadata": {"subject": "mathematics"},
                "similarity_score": 0.95
            }
        ]
        mock_service.return_value = mock_service_instance

        # 測試添加向量嵌入
        add_data = {
            "question_id": "q001",
            "question_text": "解一元一次方程式 2x + 3 = 7",
            "metadata": {
                "subject": "mathematics",
                "grade": "grade_7",
                "knowledge_points": ["algebra", "equations"],
                "difficulty": "medium"
            }
        }

        response = client.post("/api/v1/vector-search/add-embedding", json=add_data)
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 測試搜尋相似題目
        search_data = {
            "query_text": "解方程式",
            "top_k": 5,
            "metadata_filter": {"subject": "mathematics"}
        }

        response = client.post("/api/v1/vector-search/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["question_id"] == "q001"

    def test_health_check_endpoints(self):
        """測試健康檢查端點"""
        # 主服務健康檢查
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # 各模組健康檢查
        endpoints = [
            "/api/v1/weakness-analysis/health",
            "/api/v1/learning-recommendation/health", 
            "/api/v1/trend-analysis/health",
            "/api/v1/vector-search/health"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_invalid_request_handling(self):
        """測試無效請求處理"""
        # 測試無效的弱點分析請求
        invalid_data = {
            "invalid_field": "invalid_data"
        }

        response = client.post("/api/v1/weakness-analysis/analyze", json=invalid_data)
        assert response.status_code == 422  # Validation Error

        # 測試無效的端點
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404  # Not Found

    def test_cors_headers(self):
        """測試 CORS 標頭"""
        response = client.options("/api/v1/weakness-analysis/analyze")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers 