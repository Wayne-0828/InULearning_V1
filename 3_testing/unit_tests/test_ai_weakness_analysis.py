"""
Test Weakness Analysis Service

This module contains tests for the weakness analysis functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.schemas import (
    WeaknessAnalysisRequest, 
    WeaknessAnalysisResponse, 
    AnswerRecord,
    Subject,
    Grade,
    Version
)
from src.services.weakness_analysis_service import WeaknessAnalysisService


class TestWeaknessAnalysisService:
    """弱點分析服務測試"""
    
    @pytest.fixture
    def mock_db_session(self):
        """模擬資料庫會話"""
        return Mock()
    
    @pytest.fixture
    def mock_gemini_api_key(self):
        """模擬 Gemini API 金鑰"""
        return "test-api-key"
    
    @pytest.fixture
    def service(self, mock_db_session, mock_gemini_api_key):
        """創建服務實例"""
        with patch('src.services.weakness_analysis_service.ChatGoogleGenerativeAI'):
            with patch('src.services.weakness_analysis_service.AnalystAgent'):
                return WeaknessAnalysisService(mock_db_session, mock_gemini_api_key)
    
    @pytest.fixture
    def sample_request(self):
        """樣本請求數據"""
        return WeaknessAnalysisRequest(
            session_id="test-session-123",
            user_id="test-user-456",
            subject=Subject.MATH,
            grade=Grade.GRADE_7A,
            version=Version.NANYI,
            answer_records=[
                AnswerRecord(
                    question_id="q1",
                    student_answer="A",
                    is_correct=True,
                    time_spent=30,
                    confidence_score=0.8
                ),
                AnswerRecord(
                    question_id="q2",
                    student_answer="B",
                    is_correct=False,
                    time_spent=45,
                    confidence_score=0.6
                )
            ],
            total_questions=2,
            correct_count=1,
            total_time=75
        )
    
    def test_analyze_weaknesses_success(self, service, sample_request):
        """測試成功分析弱點"""
        # 模擬 AI Agent 返回結果
        mock_response = WeaknessAnalysisResponse(
            session_id=sample_request.session_id,
            user_id=sample_request.user_id,
            overall_score=75.0,
            accuracy_rate=0.5,
            average_time=37.5,
            weakness_points=[],
            learning_insights="需要加強基礎概念",
            next_steps=["繼續練習", "複習基礎概念"]
        )
        
        service.analyst_agent.analyze_weaknesses.return_value = mock_response
        
        # 執行測試
        result = service.analyze_weaknesses(sample_request)
        
        # 驗證結果
        assert result.session_id == sample_request.session_id
        assert result.user_id == sample_request.user_id
        assert result.overall_score == 75.0
        assert result.accuracy_rate == 0.5
        assert result.average_time == 37.5
        assert "需要加強基礎概念" in result.learning_insights
    
    def test_analyze_weaknesses_exception_handling(self, service, sample_request):
        """測試異常處理"""
        # 模擬 AI Agent 拋出異常
        service.analyst_agent.analyze_weaknesses.side_effect = Exception("AI service error")
        
        # 執行測試
        result = service.analyze_weaknesses(sample_request)
        
        # 驗證返回基本分析結果
        assert result.session_id == sample_request.session_id
        assert result.user_id == sample_request.user_id
        assert result.overall_score == 50.0  # 1/2 = 50%
        assert result.accuracy_rate == 0.5
        assert result.average_time == 37.5
    
    def test_get_analysis_by_session_found(self, service):
        """測試根據會話ID獲取分析結果 - 找到"""
        session_id = "test-session-123"
        
        # 模擬資料庫查詢結果
        mock_db_result = Mock()
        mock_db_result.session_id = session_id
        mock_db_result.user_id = "test-user-456"
        mock_db_result.overall_score = 80.0
        mock_db_result.accuracy_rate = 0.8
        mock_db_result.average_time = 30.0
        mock_db_result.weakness_points = []
        mock_db_result.learning_insights = "表現良好"
        mock_db_result.next_steps = ["繼續保持"]
        mock_db_result.analysis_timestamp = datetime.now()
        
        service.db_session.query.return_value.filter.return_value.first.return_value = mock_db_result
        
        # 執行測試
        result = service.get_analysis_by_session(session_id)
        
        # 驗證結果
        assert result is not None
        assert result.session_id == session_id
        assert result.overall_score == 80.0
        assert result.accuracy_rate == 0.8
    
    def test_get_analysis_by_session_not_found(self, service):
        """測試根據會話ID獲取分析結果 - 未找到"""
        session_id = "non-existent-session"
        
        # 模擬資料庫查詢返回 None
        service.db_session.query.return_value.filter.return_value.first.return_value = None
        
        # 執行測試
        result = service.get_analysis_by_session(session_id)
        
        # 驗證結果
        assert result is None
    
    def test_get_user_analysis_history(self, service):
        """測試獲取用戶分析歷史"""
        user_id = "test-user-456"
        limit = 5
        
        # 模擬資料庫查詢結果
        mock_results = []
        for i in range(3):
            mock_result = Mock()
            mock_result.session_id = f"session-{i}"
            mock_result.subject = "math"
            mock_result.overall_score = 70.0 + i * 5
            mock_result.accuracy_rate = 0.7 + i * 0.05
            mock_result.analysis_timestamp = datetime.now()
            mock_result.created_at = datetime.now()
            mock_results.append(mock_result)
        
        service.db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_results
        
        # 執行測試
        history = service.get_user_analysis_history(user_id, limit)
        
        # 驗證結果
        assert len(history) == 3
        assert history[0]["session_id"] == "session-0"
        assert history[1]["overall_score"] == 75.0
        assert history[2]["accuracy_rate"] == 0.8
    
    def test_create_basic_analysis(self, service, sample_request):
        """測試創建基本分析結果"""
        result = service._create_basic_analysis(sample_request)
        
        # 驗證結果
        assert result.session_id == sample_request.session_id
        assert result.user_id == sample_request.user_id
        assert result.overall_score == 50.0  # 1/2 = 50%
        assert result.accuracy_rate == 0.5
        assert result.average_time == 37.5
        assert len(result.weakness_points) == 1
        assert result.weakness_points[0]["knowledge_point"] == "math基礎概念"
        assert result.weakness_points[0]["weakness_level"] == "medium"
        assert "需要改進" in result.learning_insights
        assert len(result.next_steps) == 3


if __name__ == "__main__":
    pytest.main([__file__]) 