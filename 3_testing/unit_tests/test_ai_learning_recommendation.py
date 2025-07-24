import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.schemas import (
    LearningRecommendationRequest,
    LearningRecommendationResponse,
    WeaknessPoint,
    Subject,
    Grade,
    Version
)
from src.services.learning_recommendation_service import LearningRecommendationService

class TestLearningRecommendationService:
    @pytest.fixture
    def mock_db_session(self):
        return Mock()

    @pytest.fixture
    def mock_gemini_api_key(self):
        return "test-api-key"

    @pytest.fixture
    def service(self, mock_db_session, mock_gemini_api_key):
        with patch('src.services.learning_recommendation_service.ChatGoogleGenerativeAI'):
            with patch('src.services.learning_recommendation_service.TutorAgent'):
                with patch('src.services.learning_recommendation_service.RecommenderAgent'):
                    return LearningRecommendationService(mock_db_session, mock_gemini_api_key)

    @pytest.fixture
    def sample_request(self):
        return LearningRecommendationRequest(
            user_id="test-user-001",
            subject=Subject.MATHEMATICS,
            grade=Grade.GRADE_7,
            version=Version.VERSION_2024,
            weakness_points=[
                WeaknessPoint(
                    knowledge_point="algebra",
                    difficulty_level="medium",
                    error_rate=0.75,
                    description="在解一元一次方程式時經常出錯"
                )
            ],
            learning_goals=["提升代數運算能力", "加強方程式解題技巧"]
        )

    def test_generate_recommendations_success(self, service, sample_request):
        """測試成功生成學習建議"""
        with patch.object(service.tutor_agent, 'generate_recommendations') as mock_tutor:
            with patch.object(service.recommender_agent, 'find_similar_questions') as mock_recommender:
                # 模擬 AI 代理回應
                mock_tutor.return_value = LearningRecommendationResponse(
                    recommendation_id="rec-001",
                    user_id=sample_request.user_id,
                    subject=sample_request.subject,
                    grade=sample_request.grade,
                    version=sample_request.version,
                    study_plan="建議每天練習 30 分鐘代數題目",
                    recommended_questions=[],
                    created_at=datetime.now()
                )
                
                mock_recommender.return_value = []
                
                result = service.generate_recommendations(sample_request)
                
                assert result is not None
                assert result.recommendation_id == "rec-001"
                assert result.user_id == sample_request.user_id
                assert result.subject == sample_request.subject

    def test_generate_recommendations_exception_handling(self, service, sample_request):
        """測試異常處理"""
        with patch.object(service.tutor_agent, 'generate_recommendations', side_effect=Exception("AI Service Error")):
            result = service.generate_recommendations(sample_request)
            
            # 應該返回預設建議
            assert result is not None
            assert "基礎" in result.study_plan  # 預設建議包含基礎內容

    def test_get_user_recommendations(self, service):
        """測試獲取用戶建議歷史"""
        user_id = "test-user-001"
        limit = 10
        
        # 模擬資料庫查詢結果
        mock_recommendations = [
            Mock(
                id="rec-001",
                user_id=user_id,
                subject=Subject.MATHEMATICS,
                study_plan="測試建議",
                created_at=datetime.now()
            )
        ]
        
        service.db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_recommendations
        
        result = service.get_user_recommendations(user_id, limit)
        
        assert len(result) == 1
        assert result[0].id == "rec-001" 