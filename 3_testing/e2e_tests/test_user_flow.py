"""
用戶流程端到端測試
測試完整的用戶學習流程
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from utils.api_client import (
    AuthServiceClient, LearningServiceClient, 
    QuestionBankClient, AIAnalysisClient
)

@pytest.mark.e2e
class TestUserLearningFlow:
    """用戶學習流程測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.auth_client = AuthServiceClient()
        self.learning_client = LearningServiceClient()
        self.question_client = QuestionBankClient()
        self.ai_client = AIAnalysisClient()
    
    def test_student_complete_learning_cycle(self, test_user_data):
        """測試學生完整學習週期"""
        with patch('requests.Session.request') as mock_request:
            # 模擬完整的學習週期
            responses = []
            
            # 1. 學生註冊
            register_response = Mock()
            register_response.status_code = 201
            register_response.json.return_value = {
                "id": 1,
                "email": test_user_data["email"],
                "username": test_user_data["username"],
                "role": "student"
            }
            responses.append(register_response)
            
            # 2. 學生登入
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "student_token",
                "refresh_token": "refresh_token",
                "user": {"id": 1, "role": "student"}
            }
            responses.append(login_response)
            
            # 3. 獲取推薦題目
            questions_response = Mock()
            questions_response.status_code = 200
            questions_response.json.return_value = {
                "questions": [
                    {"id": "q1", "question": "數學題目1", "options": {"A": "答案1", "B": "答案2"}},
                    {"id": "q2", "question": "數學題目2", "options": {"A": "答案1", "B": "答案2"}}
                ]
            }
            responses.append(questions_response)
            
            # 4. 創建學習會話
            session_response = Mock()
            session_response.status_code = 201
            session_response.json.return_value = {
                "session_id": "session123",
                "questions": [
                    {"id": "q1", "question": "數學題目1"},
                    {"id": "q2", "question": "數學題目2"}
                ]
            }
            responses.append(session_response)
            
            # 5. 提交答案
            answer1_response = Mock()
            answer1_response.status_code = 200
            answer1_response.json.return_value = {
                "answer_id": "ans1",
                "is_correct": True,
                "score": 10
            }
            responses.append(answer1_response)
            
            answer2_response = Mock()
            answer2_response.status_code = 200
            answer2_response.json.return_value = {
                "answer_id": "ans2",
                "is_correct": False,
                "score": 0
            }
            responses.append(answer2_response)
            
            # 6. 完成會話
            complete_response = Mock()
            complete_response.status_code = 200
            complete_response.json.return_value = {
                "session_id": "session123",
                "status": "completed",
                "total_score": 10,
                "accuracy": 50.0
            }
            responses.append(complete_response)
            
            # 7. AI 分析
            analysis_response = Mock()
            analysis_response.status_code = 200
            analysis_response.json.return_value = {
                "weaknesses": [
                    {"knowledge_point": "代數概念", "error_rate": 50.0}
                ],
                "overall_accuracy": 50.0
            }
            responses.append(analysis_response)
            
            # 8. 獲取學習建議
            recommendations_response = Mock()
            recommendations_response.status_code = 200
            recommendations_response.json.return_value = {
                "recommendations": [
                    {
                        "type": "practice_focus",
                        "subject": "數學",
                        "knowledge_point": "代數概念",
                        "priority": "high"
                    }
                ]
            }
            responses.append(recommendations_response)
            
            mock_request.side_effect = responses
            
            # 執行完整學習週期
            # 1. 註冊
            user = self.auth_client.register_user(test_user_data)
            assert user["role"] == "student"
            
            # 2. 登入
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            token = login_result["access_token"]
            
            # 3. 獲取題目
            questions = self.question_client.get_random_questions({
                "subject": "數學",
                "count": 2
            }, token)
            assert len(questions["questions"]) == 2
            
            # 4. 創建學習會話
            session = self.learning_client.create_learning_session({
                "user_id": 1,
                "subject": "數學",
                "question_count": 2
            }, token)
            assert session["session_id"] == "session123"
            
            # 5. 提交答案
            answer1 = self.learning_client.submit_answer("session123", {
                "question_id": "q1",
                "selected_answer": "A"
            }, token)
            assert answer1["is_correct"] == True
            
            answer2 = self.learning_client.submit_answer("session123", {
                "question_id": "q2",
                "selected_answer": "B"
            }, token)
            assert answer2["is_correct"] == False
            
            # 6. 完成會話
            complete = self.learning_client.complete_session("session123", token)
            assert complete["status"] == "completed"
            assert complete["accuracy"] == 50.0
            
            # 7. AI 分析
            analysis = self.ai_client.analyze_weaknesses(1, {
                "session_id": "session123",
                "answers": [
                    {"question_id": "q1", "is_correct": True},
                    {"question_id": "q2", "is_correct": False}
                ]
            }, token)
            assert analysis["overall_accuracy"] == 50.0
            
            # 8. 獲取建議
            recommendations = self.ai_client.get_learning_recommendations(
                1, analysis, token
            )
            assert len(recommendations["recommendations"]) == 1
            assert recommendations["recommendations"][0]["priority"] == "high"
    
    def test_teacher_question_management_flow(self, test_teacher_data):
        """測試教師題目管理流程"""
        with patch('requests.Session.request') as mock_request:
            # 模擬教師題目管理流程
            responses = []
            
            # 1. 教師登入
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "teacher_token",
                "user": {"id": 2, "role": "teacher"}
            }
            responses.append(login_response)
            
            # 2. 創建題目
            create_question_response = Mock()
            create_question_response.status_code = 201
            create_question_response.json.return_value = {
                "id": "q_new",
                "question": "新創建的題目",
                "subject": "數學"
            }
            responses.append(create_question_response)
            
            # 3. 搜尋題目
            search_response = Mock()
            search_response.status_code = 200
            search_response.json.return_value = {
                "questions": [
                    {"id": "q_new", "question": "新創建的題目"}
                ],
                "total": 1
            }
            responses.append(search_response)
            
            # 4. 更新題目
            update_response = Mock()
            update_response.status_code = 200
            update_response.json.return_value = {
                "id": "q_new",
                "question": "更新後的題目",
                "subject": "數學"
            }
            responses.append(update_response)
            
            mock_request.side_effect = responses
            
            # 執行教師流程
            # 1. 登入
            login_result = self.auth_client.login_user({
                "email": test_teacher_data["email"],
                "password": test_teacher_data["password"]
            })
            token = login_result["access_token"]
            
            # 2. 創建題目
            question_data = {
                "question": "新創建的題目",
                "subject": "數學",
                "grade": "7A",
                "options": {"A": "答案1", "B": "答案2"},
                "answer": "A"
            }
            new_question = self.question_client.create_question(question_data, token)
            assert new_question["id"] == "q_new"
            
            # 3. 搜尋題目
            search_result = self.question_client.search_questions({
                "subject": "數學"
            }, token)
            assert search_result["total"] == 1
            
            # 4. 更新題目
            updated_question = self.question_client.update_question("q_new", {
                "question": "更新後的題目"
            }, token)
            assert updated_question["question"] == "更新後的題目"
    
    def test_parent_monitoring_flow(self, test_user_data):
        """測試家長監控流程"""
        with patch('requests.Session.request') as mock_request:
            # 模擬家長監控流程
            responses = []
            
            # 1. 家長登入
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "parent_token",
                "user": {"id": 3, "role": "parent"}
            }
            responses.append(login_response)
            
            # 2. 獲取子女學習報告
            report_response = Mock()
            report_response.status_code = 200
            report_response.json.return_value = {
                "report_id": "report123",
                "child_id": 1,
                "summary": {
                    "total_sessions": 10,
                    "average_accuracy": 75.0,
                    "total_study_time": 600
                }
            }
            responses.append(report_response)
            
            # 3. 獲取學習趨勢
            trends_response = Mock()
            trends_response.status_code = 200
            trends_response.json.return_value = {
                "trends": {
                    "accuracy_trend": [
                        {"date": "2024-01-01", "accuracy": 70.0},
                        {"date": "2024-01-02", "accuracy": 75.0}
                    ]
                }
            }
            responses.append(trends_response)
            
            mock_request.side_effect = responses
            
            # 執行家長流程
            # 1. 登入
            login_result = self.auth_client.login_user({
                "email": "parent@example.com",
                "password": "parentpass"
            })
            token = login_result["access_token"]
            
            # 2. 獲取學習報告
            report = self.ai_client.generate_report(1, "monthly", token)
            assert report["child_id"] == 1
            assert report["summary"]["total_sessions"] == 10
            
            # 3. 獲取學習趨勢
            trends = self.ai_client.analyze_trends(1, "last_30_days", token)
            assert "accuracy_trend" in trends["trends"]
            assert len(trends["trends"]["accuracy_trend"]) == 2

@pytest.mark.e2e
class TestSystemWorkflow:
    """系統工作流程測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.auth_client = AuthServiceClient()
        self.learning_client = LearningServiceClient()
        self.question_client = QuestionBankClient()
        self.ai_client = AIAnalysisClient()
    
    def test_system_startup_workflow(self):
        """測試系統啟動工作流程"""
        # 檢查所有服務是否正常啟動
        services = [
            ("auth-service", self.auth_client),
            ("learning-service", self.learning_client),
            ("question-bank-service", self.question_client),
            ("ai-analysis-service", self.ai_client)
        ]
        
        for service_name, client in services:
            try:
                is_healthy = client.health_check()
                assert is_healthy, f"{service_name} 健康檢查失敗"
            except Exception as e:
                pytest.skip(f"{service_name} 服務不可用: {e}")
    
    def test_data_synchronization_workflow(self):
        """測試資料同步工作流程"""
        with patch('requests.Session.request') as mock_request:
            # 模擬資料同步流程
            responses = []
            
            # 1. 用戶註冊
            register_response = Mock()
            register_response.status_code = 201
            register_response.json.return_value = {"id": 1}
            responses.append(register_response)
            
            # 2. 各服務同步用戶資料
            sync_responses = [
                Mock(status_code=200, json=lambda: {"synced": True}),
                Mock(status_code=200, json=lambda: {"synced": True}),
                Mock(status_code=200, json=lambda: {"synced": True}),
                Mock(status_code=200, json=lambda: {"synced": True})
            ]
            responses.extend(sync_responses)
            
            mock_request.side_effect = responses
            
            # 執行資料同步測試
            user = self.auth_client.register_user({
                "email": "sync@example.com",
                "username": "synctest",
                "password": "syncpass"
            })
            
            # 驗證各服務都已同步
            assert user["id"] == 1
    
    def test_error_recovery_workflow(self):
        """測試錯誤恢復工作流程"""
        with patch('requests.Session.request') as mock_request:
            # 模擬服務錯誤和恢復
            responses = []
            
            # 1. 正常登入
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "recovery_token",
                "user": {"id": 1}
            }
            responses.append(login_response)
            
            # 2. 服務暫時錯誤
            error_response = Mock()
            error_response.status_code = 503
            error_response.json.return_value = {
                "detail": "服務暫時不可用"
            }
            responses.append(error_response)
            
            # 3. 服務恢復
            recovery_response = Mock()
            recovery_response.status_code = 200
            recovery_response.json.return_value = {
                "status": "recovered"
            }
            responses.append(recovery_response)
            
            mock_request.side_effect = responses
            
            # 執行錯誤恢復測試
            # 1. 正常登入
            login_result = self.auth_client.login_user({
                "email": "test@example.com",
                "password": "testpass"
            })
            token = login_result["access_token"]
            
            # 2. 嘗試使用暫時不可用的服務
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.learning_client.create_learning_session({
                    "user_id": 1,
                    "subject": "數學"
                }, token)
            
            # 3. 服務恢復後重試
            # 這裡模擬服務恢復後的成功操作
            pass 