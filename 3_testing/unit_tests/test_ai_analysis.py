"""
AI 分析服務單元測試
測試弱點分析、學習建議、趨勢分析等功能
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from utils.api_client import AIAnalysisClient
from utils.test_helpers import TestHelper

@pytest.mark.unit
class TestAIAnalysisService:
    """AI 分析服務測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.ai_client = AIAnalysisClient()
        self.test_helper = TestHelper()
    
    def test_health_check(self):
        """測試健康檢查端點"""
        assert self.ai_client.health_check() == True
    
    def test_analyze_weaknesses_success(self):
        """測試分析學習弱點成功"""
        user_id = 1
        token = "test_token"
        session_data = {
            "session_id": "session123",
            "answers": [
                {"question_id": "q1", "is_correct": False, "time_spent": 45},
                {"question_id": "q2", "is_correct": True, "time_spent": 30},
                {"question_id": "q3", "is_correct": False, "time_spent": 60}
            ],
            "subject": "數學",
            "chapter": "一元一次方程式"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功分析
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "weaknesses": [
                    {
                        "knowledge_point": "方程式求解",
                        "error_rate": 66.7,
                        "common_mistakes": ["忘記移項", "計算錯誤"],
                        "recommended_practice": 5
                    },
                    {
                        "knowledge_point": "代數概念",
                        "error_rate": 50.0,
                        "common_mistakes": ["符號錯誤"],
                        "recommended_practice": 3
                    }
                ],
                "overall_accuracy": 33.3,
                "analysis_timestamp": "2024-01-01T00:00:00Z"
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.analyze_weaknesses(user_id, session_data, token)
            
            assert "weaknesses" in result
            assert len(result["weaknesses"]) == 2
            assert result["overall_accuracy"] == 33.3
            assert result["weaknesses"][0]["knowledge_point"] == "方程式求解"
    
    def test_get_learning_recommendations_success(self):
        """測試獲取學習建議成功"""
        user_id = 1
        token = "test_token"
        analysis_data = {
            "weaknesses": [
                {"knowledge_point": "方程式求解", "error_rate": 66.7}
            ],
            "overall_accuracy": 33.3
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取建議
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "recommendations": [
                    {
                        "type": "practice_focus",
                        "subject": "數學",
                        "chapter": "一元一次方程式",
                        "knowledge_point": "方程式求解",
                        "priority": "high",
                        "estimated_time": 30,
                        "resources": ["練習題", "教學影片"]
                    },
                    {
                        "type": "review_basics",
                        "subject": "數學",
                        "chapter": "基礎運算",
                        "knowledge_point": "代數概念",
                        "priority": "medium",
                        "estimated_time": 20,
                        "resources": ["複習講義"]
                    }
                ],
                "learning_path": {
                    "next_steps": ["基礎練習", "進階應用"],
                    "estimated_completion": "2週"
                }
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.get_learning_recommendations(user_id, analysis_data, token)
            
            assert "recommendations" in result
            assert len(result["recommendations"]) == 2
            assert result["recommendations"][0]["priority"] == "high"
            assert "learning_path" in result
    
    def test_analyze_trends_success(self):
        """測試分析學習趨勢成功"""
        user_id = 1
        token = "test_token"
        time_range = "last_30_days"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功分析趨勢
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "time_range": time_range,
                "trends": {
                    "accuracy_trend": [
                        {"date": "2024-01-01", "accuracy": 70.0},
                        {"date": "2024-01-15", "accuracy": 75.0},
                        {"date": "2024-01-30", "accuracy": 80.0}
                    ],
                    "study_time_trend": [
                        {"date": "2024-01-01", "minutes": 45},
                        {"date": "2024-01-15", "minutes": 60},
                        {"date": "2024-01-30", "minutes": 75}
                    ],
                    "subject_performance": {
                        "數學": {"improvement": 15.0, "sessions": 20},
                        "英文": {"improvement": 8.0, "sessions": 15}
                    }
                },
                "insights": [
                    "數學科目有顯著進步",
                    "學習時間逐漸增加",
                    "建議保持當前學習節奏"
                ]
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.analyze_trends(user_id, time_range, token)
            
            assert "trends" in result
            assert "accuracy_trend" in result["trends"]
            assert "study_time_trend" in result["trends"]
            assert "insights" in result
            assert len(result["trends"]["accuracy_trend"]) == 3
    
    def test_generate_report_success(self):
        """測試生成報告成功"""
        user_id = 1
        token = "test_token"
        report_type = "monthly"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功生成報告
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "report_type": report_type,
                "report_id": "report123",
                "generated_at": "2024-01-01T00:00:00Z",
                "summary": {
                    "total_sessions": 25,
                    "total_questions": 125,
                    "average_accuracy": 78.5,
                    "total_study_time": 1200,
                    "improvement_rate": 12.3
                },
                "detailed_analysis": {
                    "subject_breakdown": {
                        "數學": {"sessions": 15, "accuracy": 82.0},
                        "英文": {"sessions": 10, "accuracy": 74.0}
                    },
                    "weakness_areas": [
                        "方程式求解",
                        "文法概念"
                    ],
                    "strength_areas": [
                        "基礎運算",
                        "閱讀理解"
                    ]
                },
                "recommendations": [
                    "加強方程式求解練習",
                    "複習文法基礎概念"
                ]
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.generate_report(user_id, report_type, token)
            
            assert result["report_id"] == "report123"
            assert "summary" in result
            assert "detailed_analysis" in result
            assert "recommendations" in result
            assert result["summary"]["total_sessions"] == 25
    
    def test_get_ai_insights_success(self):
        """測試獲取 AI 洞察成功"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取洞察
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "insights": [
                    {
                        "type": "learning_pattern",
                        "title": "最佳學習時段",
                        "description": "您在晚上 7-9 點的學習效率最高",
                        "confidence": 0.85,
                        "actionable": True
                    },
                    {
                        "type": "performance_prediction",
                        "title": "預測表現",
                        "description": "如果保持當前學習節奏，下個月準確率可能達到 85%",
                        "confidence": 0.78,
                        "actionable": False
                    },
                    {
                        "type": "study_optimization",
                        "title": "學習優化建議",
                        "description": "建議每天練習 30 分鐘，效果最佳",
                        "confidence": 0.92,
                        "actionable": True
                    }
                ],
                "generated_at": "2024-01-01T00:00:00Z"
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.get_ai_insights(user_id, token)
            
            assert "insights" in result
            assert len(result["insights"]) == 3
            assert result["insights"][0]["type"] == "learning_pattern"
            assert result["insights"][0]["actionable"] == True
    
    def test_analyze_weaknesses_no_data(self):
        """測試分析弱點但無資料"""
        user_id = 1
        token = "test_token"
        empty_session_data = {
            "session_id": "session123",
            "answers": [],
            "subject": "數學"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無資料錯誤
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "沒有足夠的資料進行分析"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.ai_client.analyze_weaknesses(user_id, empty_session_data, token)
    
    def test_analyze_trends_insufficient_data(self):
        """測試分析趨勢但資料不足"""
        user_id = 999
        token = "test_token"
        time_range = "last_30_days"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬資料不足
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "學習資料不足，無法進行趨勢分析"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.ai_client.analyze_trends(user_id, time_range, token)
    
    def test_generate_report_invalid_type(self):
        """測試生成無效類型的報告"""
        user_id = 1
        token = "test_token"
        invalid_report_type = "invalid_type"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無效報告類型
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "不支援的報告類型"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.ai_client.generate_report(user_id, invalid_report_type, token)
    
    def test_invalid_token_access(self):
        """測試無效 token 存取"""
        user_id = 1
        invalid_token = "invalid_token"
        session_data = {"session_id": "session123", "answers": []}
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無效 token 錯誤
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "detail": "無效的認證憑證"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.ai_client.analyze_weaknesses(user_id, session_data, invalid_token)
    
    @pytest.mark.parametrize("invalid_session_data", [
        {},  # 空資料
        {"session_id": "session123"},  # 缺少必要欄位
        {"session_id": "session123", "answers": "invalid"},  # 無效答案格式
    ])
    def test_analyze_weaknesses_invalid_data(self, invalid_session_data):
        """測試分析弱點無效資料"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬驗證錯誤
            mock_response = Mock()
            mock_response.status_code = 422
            mock_response.json.return_value = {
                "detail": "資料驗證失敗"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.ai_client.analyze_weaknesses(user_id, invalid_session_data, token)

@pytest.mark.unit
class TestAIAnalysisIntegration:
    """AI 分析服務整合測試"""
    
    def setup_method(self):
        """測試前設定"""
        self.ai_client = AIAnalysisClient()
    
    def test_complete_analysis_flow(self):
        """測試完整分析流程"""
        user_id = 1
        token = "test_token"
        session_data = {
            "session_id": "session123",
            "answers": [
                {"question_id": "q1", "is_correct": False},
                {"question_id": "q2", "is_correct": True}
            ],
            "subject": "數學"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬弱點分析成功
            weakness_response = Mock()
            weakness_response.status_code = 200
            weakness_response.json.return_value = {
                "weaknesses": [{"knowledge_point": "方程式求解", "error_rate": 50.0}],
                "overall_accuracy": 50.0
            }
            
            # 模擬獲取建議成功
            recommendation_response = Mock()
            recommendation_response.status_code = 200
            recommendation_response.json.return_value = {
                "recommendations": [
                    {"type": "practice_focus", "priority": "high"}
                ]
            }
            
            # 模擬趨勢分析成功
            trend_response = Mock()
            trend_response.status_code = 200
            trend_response.json.return_value = {
                "trends": {"accuracy_trend": []},
                "insights": ["有進步空間"]
            }
            
            # 模擬生成報告成功
            report_response = Mock()
            report_response.status_code = 200
            report_response.json.return_value = {
                "report_id": "report123",
                "summary": {"total_sessions": 10}
            }
            
            mock_request.side_effect = [
                weakness_response, recommendation_response, 
                trend_response, report_response
            ]
            
            # 執行完整分析流程
            # 1. 分析弱點
            weakness_result = self.ai_client.analyze_weaknesses(user_id, session_data, token)
            assert "weaknesses" in weakness_result
            
            # 2. 獲取學習建議
            recommendation_result = self.ai_client.get_learning_recommendations(
                user_id, weakness_result, token
            )
            assert "recommendations" in recommendation_result
            
            # 3. 分析趨勢
            trend_result = self.ai_client.analyze_trends(user_id, "last_30_days", token)
            assert "trends" in trend_result
            
            # 4. 生成報告
            report_result = self.ai_client.generate_report(user_id, "monthly", token)
            assert report_result["report_id"] == "report123"
    
    def test_ai_insights_integration(self):
        """測試 AI 洞察整合"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬獲取洞察成功
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "insights": [
                    {
                        "type": "learning_pattern",
                        "title": "學習模式分析",
                        "actionable": True
                    }
                ]
            }
            mock_request.return_value = mock_response
            
            result = self.ai_client.get_ai_insights(user_id, token)
            
            assert "insights" in result
            assert result["insights"][0]["actionable"] == True 