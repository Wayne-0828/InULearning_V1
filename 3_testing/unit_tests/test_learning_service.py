"""
學習服務單元測試
測試學習會話、答案提交、進度追蹤等功能
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from utils.api_client import LearningServiceClient
from utils.test_helpers import TestHelper

@pytest.mark.unit
class TestLearningService:
    """學習服務測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.learning_client = LearningServiceClient()
        self.test_helper = TestHelper()
    
    def test_health_check(self):
        """測試健康檢查端點"""
        assert self.learning_client.health_check() == True
    
    def test_create_learning_session_success(self, test_learning_session_data):
        """測試創建學習會話成功"""
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功創建
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "session_id": "session123",
                "user_id": test_learning_session_data["user_id"],
                "grade": test_learning_session_data["grade"],
                "subject": test_learning_session_data["subject"],
                "question_count": test_learning_session_data["question_count"],
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.create_learning_session(test_learning_session_data, token)
            
            assert result["session_id"] == "session123"
            assert result["user_id"] == test_learning_session_data["user_id"]
            assert result["status"] == "active"
    
    def test_get_learning_session_success(self):
        """測試獲取學習會話成功"""
        session_id = "session123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "session_id": session_id,
                "user_id": 1,
                "grade": "7A",
                "subject": "數學",
                "question_count": 5,
                "completed_questions": 2,
                "status": "active",
                "questions": [
                    {"id": "q1", "question": "題目1", "answered": True},
                    {"id": "q2", "question": "題目2", "answered": False}
                ]
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.get_learning_session(session_id, token)
            
            assert result["session_id"] == session_id
            assert "questions" in result
            assert result["completed_questions"] == 2
    
    def test_get_learning_session_not_found(self):
        """測試獲取不存在的學習會話"""
        session_id = "nonexistent"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬會話不存在
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "detail": "學習會話不存在"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.get_learning_session(session_id, token)
    
    def test_submit_answer_success(self):
        """測試提交答案成功"""
        session_id = "session123"
        token = "test_token"
        answer_data = {
            "question_id": "q1",
            "selected_answer": "A",
            "time_spent": 30
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功提交
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "answer_id": "ans123",
                "question_id": "q1",
                "is_correct": True,
                "correct_answer": "A",
                "explanation": "答案正確",
                "score": 10,
                "time_spent": 30
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.submit_answer(session_id, answer_data, token)
            
            assert result["answer_id"] == "ans123"
            assert result["is_correct"] == True
            assert result["score"] == 10
    
    def test_submit_answer_incorrect(self):
        """測試提交錯誤答案"""
        session_id = "session123"
        token = "test_token"
        answer_data = {
            "question_id": "q1",
            "selected_answer": "B",
            "time_spent": 45
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬錯誤答案
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "answer_id": "ans123",
                "question_id": "q1",
                "is_correct": False,
                "correct_answer": "A",
                "explanation": "正確答案是 A，因為...",
                "score": 0,
                "time_spent": 45
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.submit_answer(session_id, answer_data, token)
            
            assert result["is_correct"] == False
            assert result["correct_answer"] == "A"
            assert result["score"] == 0
    
    def test_get_session_progress_success(self):
        """測試獲取會話進度成功"""
        session_id = "session123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取進度
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "session_id": session_id,
                "total_questions": 5,
                "completed_questions": 3,
                "correct_answers": 2,
                "total_score": 20,
                "progress_percentage": 60,
                "estimated_time_remaining": 10
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.get_session_progress(session_id, token)
            
            assert result["total_questions"] == 5
            assert result["completed_questions"] == 3
            assert result["progress_percentage"] == 60
    
    def test_complete_session_success(self):
        """測試完成學習會話成功"""
        session_id = "session123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功完成
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "session_id": session_id,
                "status": "completed",
                "total_score": 40,
                "accuracy": 80.0,
                "completion_time": "2024-01-01T01:00:00Z",
                "summary": {
                    "total_questions": 5,
                    "correct_answers": 4,
                    "average_time": 45
                }
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.complete_session(session_id, token)
            
            assert result["status"] == "completed"
            assert result["total_score"] == 40
            assert result["accuracy"] == 80.0
    
    def test_get_learning_recommendations_success(self):
        """測試獲取學習建議成功"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取建議
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "recommendations": [
                    {
                        "type": "weakness_focus",
                        "subject": "數學",
                        "chapter": "一元一次方程式",
                        "reason": "最近在此章節表現較差",
                        "priority": "high"
                    },
                    {
                        "type": "practice_more",
                        "subject": "英文",
                        "chapter": "文法",
                        "reason": "需要更多練習",
                        "priority": "medium"
                    }
                ],
                "generated_at": "2024-01-01T00:00:00Z"
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.get_learning_recommendations(user_id, token)
            
            assert "recommendations" in result
            assert len(result["recommendations"]) == 2
            assert result["recommendations"][0]["priority"] == "high"
    
    def test_get_learning_trends_success(self):
        """測試獲取學習趨勢成功"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取趨勢
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": user_id,
                "trends": {
                    "daily_activity": [
                        {"date": "2024-01-01", "sessions": 3, "questions": 15},
                        {"date": "2024-01-02", "sessions": 2, "questions": 10}
                    ],
                    "subject_performance": {
                        "數學": {"accuracy": 85.0, "sessions": 10},
                        "英文": {"accuracy": 78.0, "sessions": 8}
                    },
                    "improvement_rate": 12.5
                },
                "period": "last_30_days"
            }
            mock_request.return_value = mock_response
            
            result = self.learning_client.get_learning_trends(user_id, token)
            
            assert "trends" in result
            assert "daily_activity" in result["trends"]
            assert "subject_performance" in result["trends"]
            assert result["trends"]["improvement_rate"] == 12.5
    
    def test_submit_answer_invalid_session(self):
        """測試向無效會話提交答案"""
        session_id = "invalid_session"
        token = "test_token"
        answer_data = {
            "question_id": "q1",
            "selected_answer": "A"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無效會話錯誤
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "無效的學習會話"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.submit_answer(session_id, answer_data, token)
    
    def test_complete_session_not_all_questions_answered(self):
        """測試完成會話但未答完所有題目"""
        session_id = "session123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬未完成所有題目
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "還有未完成的題目"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.complete_session(session_id, token)
    
    def test_invalid_token_access(self, test_learning_session_data):
        """測試無效 token 存取"""
        invalid_token = "invalid_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無效 token 錯誤
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "detail": "無效的認證憑證"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.create_learning_session(test_learning_session_data, invalid_token)
    
    @pytest.mark.parametrize("invalid_session_data", [
        {"user_id": 1},  # 缺少必要欄位
        {"user_id": 1, "grade": "invalid_grade"},  # 無效年級
        {"user_id": 1, "question_count": 0},  # 無效題目數量
        {}  # 空資料
    ])
    def test_create_session_invalid_data(self, invalid_session_data):
        """測試創建會話無效資料"""
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
                self.learning_client.create_learning_session(invalid_session_data, token)

@pytest.mark.unit
class TestLearningServiceIntegration:
    """學習服務整合測試"""
    
    def setup_method(self):
        """測試前設定"""
        self.learning_client = LearningServiceClient()
    
    def test_complete_learning_flow(self, test_learning_session_data):
        """測試完整學習流程"""
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬創建會話成功
            create_response = Mock()
            create_response.status_code = 201
            create_response.json.return_value = {
                "session_id": "session123",
                "user_id": test_learning_session_data["user_id"],
                "status": "active"
            }
            
            # 模擬獲取會話成功
            get_response = Mock()
            get_response.status_code = 200
            get_response.json.return_value = {
                "session_id": "session123",
                "questions": [{"id": "q1", "question": "題目1"}]
            }
            
            # 模擬提交答案成功
            answer_response = Mock()
            answer_response.status_code = 200
            answer_response.json.return_value = {
                "answer_id": "ans123",
                "is_correct": True
            }
            
            # 模擬獲取進度成功
            progress_response = Mock()
            progress_response.status_code = 200
            progress_response.json.return_value = {
                "completed_questions": 1,
                "total_questions": 1
            }
            
            # 模擬完成會話成功
            complete_response = Mock()
            complete_response.status_code = 200
            complete_response.json.return_value = {
                "session_id": "session123",
                "status": "completed",
                "total_score": 10
            }
            
            mock_request.side_effect = [
                create_response, get_response, answer_response, 
                progress_response, complete_response
            ]
            
            # 執行完整學習流程
            # 1. 創建學習會話
            session_result = self.learning_client.create_learning_session(test_learning_session_data, token)
            assert session_result["session_id"] == "session123"
            
            # 2. 獲取會話
            session_data = self.learning_client.get_learning_session("session123", token)
            assert "questions" in session_data
            
            # 3. 提交答案
            answer_result = self.learning_client.submit_answer("session123", {
                "question_id": "q1",
                "selected_answer": "A"
            }, token)
            assert answer_result["is_correct"] == True
            
            # 4. 檢查進度
            progress_result = self.learning_client.get_session_progress("session123", token)
            assert progress_result["completed_questions"] == 1
            
            # 5. 完成會話
            complete_result = self.learning_client.complete_session("session123", token)
            assert complete_result["status"] == "completed" 