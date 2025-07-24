import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.schemas import (
    TrendAnalysisRequest,
    TrendAnalysisResponse,
    Subject,
    Grade,
    Version
)
from src.services.trend_analysis_service import TrendAnalysisService

class TestTrendAnalysisService:
    @pytest.fixture
    def mock_db_session(self):
        return Mock()

    @pytest.fixture
    def mock_gemini_api_key(self):
        return "test-api-key"

    @pytest.fixture
    def service(self, mock_db_session, mock_gemini_api_key):
        with patch('src.services.trend_analysis_service.ChatGoogleGenerativeAI'):
            with patch('src.services.trend_analysis_service.TrendAnalyzerAgent'):
                return TrendAnalysisService(mock_db_session, mock_gemini_api_key)

    @pytest.fixture
    def sample_request(self):
        return TrendAnalysisRequest(
            user_id="test-user-001",
            subject=Subject.MATHEMATICS,
            grade=Grade.GRADE_7,
            version=Version.VERSION_2024,
            time_range="last_30_days"
        )

    def test_analyze_trends_success(self, service, sample_request):
        """測試成功分析學習趨勢"""
        with patch.object(service.trend_analyzer_agent, 'analyze_trends') as mock_analyzer:
            # 模擬 AI 代理回應
            mock_analyzer.return_value = TrendAnalysisResponse(
                analysis_id="trend-001",
                user_id=sample_request.user_id,
                subject=sample_request.subject,
                grade=sample_request.grade,
                version=sample_request.version,
                time_range=sample_request.time_range,
                overall_trend="進步",
                subject_performance={
                    "algebra": "良好",
                    "geometry": "需要加強"
                },
                recommendations=["建議增加幾何練習時間"],
                created_at=datetime.now()
            )
            
            result = service.analyze_trends(sample_request)
            
            assert result is not None
            assert result.analysis_id == "trend-001"
            assert result.user_id == sample_request.user_id
            assert result.subject == sample_request.subject
            assert result.overall_trend == "進步"

    def test_analyze_trends_exception_handling(self, service, sample_request):
        """測試異常處理"""
        with patch.object(service.trend_analyzer_agent, 'analyze_trends', side_effect=Exception("AI Service Error")):
            result = service.analyze_trends(sample_request)
            
            # 應該返回預設分析
            assert result is not None
            assert "基礎" in result.overall_trend  # 預設分析包含基礎內容

    def test_get_user_trends(self, service):
        """測試獲取用戶趨勢歷史"""
        user_id = "test-user-001"
        limit = 10
        
        # 模擬資料庫查詢結果
        mock_trends = [
            Mock(
                id="trend-001",
                user_id=user_id,
                subject=Subject.MATHEMATICS,
                overall_trend="進步",
                created_at=datetime.now()
            )
        ]
        
        service.db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_trends
        
        result = service.get_user_trends(user_id, limit)
        
        assert len(result) == 1
        assert result[0].id == "trend-001"
        assert result[0].overall_trend == "進步" 