"""
API 整合測試
測試跨服務的 API 互動和端到端流程
"""

import pytest
import json
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from utils.api_client import (
    AuthServiceClient, LearningServiceClient, 
    QuestionBankClient, AIAnalysisClient
)
from utils.test_helpers import TestHelper

@pytest.mark.integration
class TestAPIIntegration:
    """API 整合測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.auth_client = AuthServiceClient()
        self.learning_client = LearningServiceClient()
        self.question_client = QuestionBankClient()
        self.ai_client = AIAnalysisClient()
        self.test_helper = TestHelper()
    
    def test_complete_user_learning_flow(self, test_user_data, test_question_data, test_learning_session_data):
        """測試完整用戶學習流程"""
        with patch('requests.Session.request') as mock_request:
            # 模擬所有服務的回應
            responses = []
            
            # 1. 用戶註冊
            register_response = Mock()
            register_response.status_code = 201
            register_response.json.return_value = {
                "id": 1,
                "email": test_user_data["email"],
                "username": test_user_data["username"]
            }
            responses.append(register_response)
            
            # 2. 用戶登入
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "test_token_123",
                "refresh_token": "refresh_token_123",
                "user": {"id": 1, "email": test_user_data["email"]}
            }
            responses.append(login_response)
            
            # 3. 創建題目
            create_question_response = Mock()
            create_question_response.status_code = 201
            create_question_response.json.return_value = {
                "id": "q123",
                "question": test_question_data["question"]
            }
            responses.append(create_question_response)
            
            # 4. 創建學習會話
            create_session_response = Mock()
            create_session_response.status_code = 201
            create_session_response.json.return_value = {
                "session_id": "session123",
                "user_id": 1,
                "questions": [{"id": "q123", "question": test_question_data["question"]}]
            }
            responses.append(create_session_response)
            
            # 5. 提交答案
            submit_answer_response = Mock()
            submit_answer_response.status_code = 200
            submit_answer_response.json.return_value = {
                "answer_id": "ans123",
                "is_correct": True,
                "score": 10
            }
            responses.append(submit_answer_response)
            
            # 6. 完成會話
            complete_session_response = Mock()
            complete_session_response.status_code = 200
            complete_session_response.json.return_value = {
                "session_id": "session123",
                "status": "completed",
                "total_score": 10
            }
            responses.append(complete_session_response)
            
            # 7. 分析弱點
            analyze_weakness_response = Mock()
            analyze_weakness_response.status_code = 200
            analyze_weakness_response.json.return_value = {
                "weaknesses": [{"knowledge_point": "方程式求解", "error_rate": 0.0}],
                "overall_accuracy": 100.0
            }
            responses.append(analyze_weakness_response)
            
            # 8. 獲取學習建議
            recommendations_response = Mock()
            recommendations_response.status_code = 200
            recommendations_response.json.return_value = {
                "recommendations": [
                    {"type": "continue_practice", "priority": "low"}
                ]
            }
            responses.append(recommendations_response)
            
            mock_request.side_effect = responses
            
            # 執行完整流程
            # 1. 用戶註冊
            register_result = self.auth_client.register_user(test_user_data)
            assert register_result["id"] == 1
            
            # 2. 用戶登入
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            token = login_result["access_token"]
            assert token == "test_token_123"
            
            # 3. 創建題目
            question_result = self.question_client.create_question(test_question_data, token)
            assert question_result["id"] == "q123"
            
            # 4. 創建學習會話
            session_result = self.learning_client.create_learning_session(test_learning_session_data, token)
            assert session_result["session_id"] == "session123"
            
            # 5. 提交答案
            answer_result = self.learning_client.submit_answer("session123", {
                "question_id": "q123",
                "selected_answer": "A"
            }, token)
            assert answer_result["is_correct"] == True
            
            # 6. 完成會話
            complete_result = self.learning_client.complete_session("session123", token)
            assert complete_result["status"] == "completed"
            
            # 7. 分析弱點
            weakness_result = self.ai_client.analyze_weaknesses(1, {
                "session_id": "session123",
                "answers": [{"question_id": "q123", "is_correct": True}]
            }, token)
            assert weakness_result["overall_accuracy"] == 100.0
            
            # 8. 獲取學習建議
            recommendations_result = self.ai_client.get_learning_recommendations(
                1, weakness_result, token
            )
            assert len(recommendations_result["recommendations"]) == 1
    
    def test_cross_service_authentication(self, test_user_data):
        """測試跨服務認證"""
        with patch('requests.Session.request') as mock_request:
            # 模擬登入成功
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "cross_service_token",
                "user": {"id": 1, "email": test_user_data["email"]}
            }
            
            # 模擬各服務的認證檢查
            auth_check_responses = [
                Mock(status_code=200, json=lambda: {"valid": True}),
                Mock(status_code=200, json=lambda: {"valid": True}),
                Mock(status_code=200, json=lambda: {"valid": True}),
                Mock(status_code=200, json=lambda: {"valid": True})
            ]
            
            mock_request.side_effect = [login_response] + auth_check_responses
            
            # 登入獲取 token
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            token = login_result["access_token"]
            
            # 測試各服務都能使用同一個 token
            assert self.auth_client.get_user_profile(1, token) is not None
            assert self.learning_client.get_learning_recommendations(1, token) is not None
            assert self.question_client.get_chapters("數學", "7A", token) is not None
            assert self.ai_client.get_ai_insights(1, token) is not None
    
    def test_service_communication_failure(self, test_user_data):
        """測試服務間通訊失敗"""
        with patch('requests.Session.request') as mock_request:
            # 模擬登入成功
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "test_token",
                "user": {"id": 1}
            }
            
            # 模擬學習服務失敗
            learning_failure_response = Mock()
            learning_failure_response.status_code = 503
            learning_failure_response.json.return_value = {
                "detail": "學習服務暫時不可用"
            }
            
            mock_request.side_effect = [login_response, learning_failure_response]
            
            # 登入
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            token = login_result["access_token"]
            
            # 嘗試使用學習服務，應該失敗
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.create_learning_session({
                    "user_id": 1,
                    "grade": "7A",
                    "subject": "數學"
                }, token)
    
    def test_data_consistency_across_services(self, test_user_data):
        """測試跨服務資料一致性"""
        with patch('requests.Session.request') as mock_request:
            # 模擬用戶資料在不同服務中的一致性
            user_id = 1
            
            # 認證服務中的用戶資料
            auth_user_response = Mock()
            auth_user_response.status_code = 200
            auth_user_response.json.return_value = {
                "id": user_id,
                "email": test_user_data["email"],
                "username": test_user_data["username"],
                "grade": test_user_data["grade"]
            }
            
            # 學習服務中的用戶資料
            learning_user_response = Mock()
            learning_user_response.status_code = 200
            learning_user_response.json.return_value = {
                "user_id": user_id,
                "grade": test_user_data["grade"],
                "learning_history": []
            }
            
            # AI 分析服務中的用戶資料
            ai_user_response = Mock()
            ai_user_response.status_code = 200
            ai_user_response.json.return_value = {
                "user_id": user_id,
                "analysis_data": {
                    "grade": test_user_data["grade"],
                    "performance": {}
                }
            }
            
            mock_request.side_effect = [
                auth_user_response, learning_user_response, ai_user_response
            ]
            
            # 驗證各服務中的用戶資料一致性
            auth_user = self.auth_client.get_user_profile(user_id, "test_token")
            learning_user = self.learning_client.get_learning_recommendations(user_id, "test_token")
            ai_user = self.ai_client.get_ai_insights(user_id, "test_token")
            
            # 檢查年級資訊一致性
            assert auth_user["grade"] == test_user_data["grade"]
            assert learning_user["user_id"] == user_id
            assert ai_user["user_id"] == user_id
    
    def test_error_propagation_across_services(self, test_user_data):
        """測試錯誤在服務間的傳播"""
        with patch('requests.Session.request') as mock_request:
            # 模擬題庫服務錯誤影響學習服務
            question_error_response = Mock()
            question_error_response.status_code = 500
            question_error_response.json.return_value = {
                "detail": "題庫服務內部錯誤"
            }
            
            # 模擬學習服務因為無法獲取題目而失敗
            learning_error_response = Mock()
            learning_error_response.status_code = 503
            learning_error_response.json.return_value = {
                "detail": "無法從題庫服務獲取題目"
            }
            
            mock_request.side_effect = [question_error_response, learning_error_response]
            
            # 題庫服務錯誤
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.question_client.get_random_questions({
                    "subject": "數學",
                    "count": 5
                }, "test_token")
            
            # 學習服務也受影響
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.create_learning_session({
                    "user_id": 1,
                    "subject": "數學"
                }, "test_token")
    
    def test_concurrent_service_requests(self, test_user_data):
        """測試並發服務請求"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(service_name, client, method, *args):
            """並發請求函數"""
            try:
                with patch('requests.Session.request') as mock_request:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "service": service_name,
                        "status": "success"
                    }
                    mock_request.return_value = mock_response
                    
                    result = method(*args)
                    results.append((service_name, result))
            except Exception as e:
                errors.append((service_name, str(e)))
        
        # 創建並發請求
        threads = []
        
        # 認證服務請求
        t1 = threading.Thread(
            target=make_request,
            args=("auth", self.auth_client, self.auth_client.get_user_profile, 1, "token")
        )
        threads.append(t1)
        
        # 學習服務請求
        t2 = threading.Thread(
            target=make_request,
            args=("learning", self.learning_client, self.learning_client.get_learning_recommendations, 1, "token")
        )
        threads.append(t2)
        
        # 題庫服務請求
        t3 = threading.Thread(
            target=make_request,
            args=("question", self.question_client, self.question_client.get_chapters, "數學", "7A", "token")
        )
        threads.append(t3)
        
        # 啟動所有線程
        for t in threads:
            t.start()
        
        # 等待所有線程完成
        for t in threads:
            t.join()
        
        # 驗證結果
        assert len(results) == 3
        assert len(errors) == 0
        
        service_names = [r[0] for r in results]
        assert "auth" in service_names
        assert "learning" in service_names
        assert "question" in service_names
    
    def test_service_health_check_integration(self):
        """測試服務健康檢查整合"""
        with patch('requests.Session.request') as mock_request:
            # 模擬所有服務健康檢查
            health_responses = [
                Mock(status_code=200, json=lambda: {"status": "healthy"}),
                Mock(status_code=200, json=lambda: {"status": "healthy"}),
                Mock(status_code=200, json=lambda: {"status": "healthy"}),
                Mock(status_code=200, json=lambda: {"status": "healthy"})
            ]
            
            mock_request.side_effect = health_responses
            
            # 檢查所有服務健康狀態
            auth_healthy = self.auth_client.health_check()
            learning_healthy = self.learning_client.health_check()
            question_healthy = self.question_client.health_check()
            ai_healthy = self.ai_client.health_check()
            
            assert auth_healthy == True
            assert learning_healthy == True
            assert question_healthy == True
            assert ai_healthy == True
    
    def test_api_version_compatibility(self, test_user_data):
        """測試 API 版本相容性"""
        with patch('requests.Session.request') as mock_request:
            # 模擬不同版本的 API 回應
            v1_response = Mock()
            v1_response.status_code = 200
            v1_response.json.return_value = {
                "version": "v1.0",
                "data": {"user_id": 1}
            }
            
            v2_response = Mock()
            v2_response.status_code = 200
            v2_response.json.return_value = {
                "version": "v2.0",
                "data": {"user_id": 1, "additional_field": "new"}
            }
            
            mock_request.side_effect = [v1_response, v2_response]
            
            # 測試 v1 API
            v1_result = self.auth_client.get_user_profile(1, "token")
            assert v1_result["version"] == "v1.0"
            
            # 測試 v2 API
            v2_result = self.learning_client.get_learning_recommendations(1, "token")
            assert v2_result["version"] == "v2.0"
            assert "additional_field" in v2_result["data"]
    
    def test_rate_limiting_across_services(self, test_user_data):
        """測試跨服務的速率限制"""
        with patch('requests.Session.request') as mock_request:
            # 模擬速率限制錯誤
            rate_limit_response = Mock()
            rate_limit_response.status_code = 429
            rate_limit_response.json.return_value = {
                "detail": "請求過於頻繁，請稍後再試",
                "retry_after": 60
            }
            
            mock_request.return_value = rate_limit_response
            
            # 測試速率限制處理
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.auth_client.register_user(test_user_data)
            
            # 驗證錯誤訊息包含重試資訊
            try:
                self.auth_client.register_user(test_user_data)
            except ValueError as e:
                assert "429" in str(e)
    
    def test_service_dependency_chain(self, test_user_data):
        """測試服務依賴鏈"""
        with patch('requests.Session.request') as mock_request:
            # 模擬服務依賴鏈：認證 -> 題庫 -> 學習 -> AI 分析
            responses = []
            
            # 1. 認證服務
            auth_response = Mock()
            auth_response.status_code = 200
            auth_response.json.return_value = {
                "access_token": "chain_token",
                "user": {"id": 1}
            }
            responses.append(auth_response)
            
            # 2. 題庫服務
            question_response = Mock()
            question_response.status_code = 200
            question_response.json.return_value = {
                "questions": [{"id": "q1", "question": "測試題目"}]
            }
            responses.append(question_response)
            
            # 3. 學習服務
            learning_response = Mock()
            learning_response.status_code = 200
            learning_response.json.return_value = {
                "session_id": "chain_session",
                "questions": [{"id": "q1"}]
            }
            responses.append(learning_response)
            
            # 4. AI 分析服務
            ai_response = Mock()
            ai_response.status_code = 200
            ai_response.json.return_value = {
                "analysis": "基於學習會話的分析結果"
            }
            responses.append(ai_response)
            
            mock_request.side_effect = responses
            
            # 執行依賴鏈
            # 1. 登入
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            token = login_result["access_token"]
            
            # 2. 獲取題目
            questions = self.question_client.get_random_questions({
                "subject": "數學",
                "count": 1
            }, token)
            
            # 3. 創建學習會話
            session = self.learning_client.create_learning_session({
                "user_id": 1,
                "subject": "數學"
            }, token)
            
            # 4. AI 分析
            analysis = self.ai_client.analyze_weaknesses(1, {
                "session_id": session["session_id"],
                "answers": []
            }, token)
            
            # 驗證依賴鏈完整性
            assert token == "chain_token"
            assert len(questions["questions"]) == 1
            assert session["session_id"] == "chain_session"
            assert "analysis" in analysis 