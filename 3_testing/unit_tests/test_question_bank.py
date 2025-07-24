"""
題庫服務單元測試
測試題目管理、搜尋、章節等功能
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from utils.api_client import QuestionBankClient
from utils.test_helpers import TestHelper

@pytest.mark.unit
class TestQuestionBankService:
    """題庫服務測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.question_client = QuestionBankClient()
        self.test_helper = TestHelper()
    
    def test_health_check(self):
        """測試健康檢查端點"""
        assert self.question_client.health_check() == True
    
    def test_create_question_success(self, test_question_data):
        """測試創建題目成功"""
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功創建
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "id": "q123",
                "question": test_question_data["question"],
                "grade": test_question_data["grade"],
                "subject": test_question_data["subject"],
                "message": "題目創建成功"
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.create_question(test_question_data, token)
            
            assert result["id"] == "q123"
            assert result["question"] == test_question_data["question"]
            assert result["grade"] == test_question_data["grade"]
    
    def test_get_question_success(self):
        """測試獲取題目成功"""
        question_id = "q123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": question_id,
                "question": "解下列方程式：2x + 5 = 13",
                "options": {"A": "x = 4", "B": "x = 6", "C": "x = 8", "D": "x = 10"},
                "answer": "A",
                "explanation": "解一元一次方程式..."
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.get_question(question_id, token)
            
            assert result["id"] == question_id
            assert "question" in result
            assert "options" in result
            assert "answer" in result
    
    def test_get_question_not_found(self):
        """測試獲取不存在的題目"""
        question_id = "nonexistent"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬題目不存在
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "detail": "題目不存在"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.question_client.get_question(question_id, token)
    
    def test_update_question_success(self, test_question_data):
        """測試更新題目成功"""
        question_id = "q123"
        token = "test_token"
        updated_data = {
            "question": "更新後的題目",
            "explanation": "更新後的解釋"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功更新
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": question_id,
                "question": "更新後的題目",
                "explanation": "更新後的解釋",
                "message": "題目更新成功"
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.update_question(question_id, updated_data, token)
            
            assert result["question"] == "更新後的題目"
            assert result["explanation"] == "更新後的解釋"
    
    def test_delete_question_success(self):
        """測試刪除題目成功"""
        question_id = "q123"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功刪除
            mock_response = Mock()
            mock_response.status_code = 204
            mock_request.return_value = mock_response
            
            result = self.question_client.delete_question(question_id, token)
            
            assert result == True
    
    def test_search_questions_success(self):
        """測試搜尋題目成功"""
        token = "test_token"
        search_params = {
            "subject": "數學",
            "grade": "7A",
            "difficulty": "normal",
            "limit": 10
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功搜尋
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "questions": [
                    {
                        "id": "q1",
                        "question": "題目1",
                        "grade": "7A",
                        "subject": "數學"
                    },
                    {
                        "id": "q2",
                        "question": "題目2",
                        "grade": "7A",
                        "subject": "數學"
                    }
                ],
                "total": 2,
                "page": 1,
                "limit": 10
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.search_questions(search_params, token)
            
            assert "questions" in result
            assert len(result["questions"]) == 2
            assert result["total"] == 2
    
    def test_get_random_questions_success(self):
        """測試獲取隨機題目成功"""
        token = "test_token"
        params = {
            "subject": "數學",
            "grade": "7A",
            "count": 5,
            "difficulty": "normal"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取隨機題目
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "questions": [
                    {"id": f"q{i}", "question": f"隨機題目{i}"} 
                    for i in range(1, 6)
                ],
                "count": 5
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.get_random_questions(params, token)
            
            assert "questions" in result
            assert len(result["questions"]) == 5
            assert result["count"] == 5
    
    def test_get_chapters_success(self):
        """測試獲取章節列表成功"""
        token = "test_token"
        subject = "數學"
        grade = "7A"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取章節
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "chapters": [
                    {"id": "ch1", "name": "第一章 一元一次方程式", "order": 1},
                    {"id": "ch2", "name": "第二章 二元一次方程式", "order": 2}
                ],
                "subject": subject,
                "grade": grade
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.get_chapters(subject, grade, token)
            
            assert "chapters" in result
            assert len(result["chapters"]) == 2
            assert result["subject"] == subject
            assert result["grade"] == grade
    
    def test_get_knowledge_points_success(self):
        """測試獲取知識點成功"""
        chapter_id = "ch1"
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取知識點
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "knowledge_points": [
                    {"id": "kp1", "name": "方程式求解", "description": "解一元一次方程式"},
                    {"id": "kp2", "name": "移項法則", "description": "等式的移項操作"}
                ],
                "chapter_id": chapter_id
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.get_knowledge_points(chapter_id, token)
            
            assert "knowledge_points" in result
            assert len(result["knowledge_points"]) == 2
            assert result["chapter_id"] == chapter_id
    
    def test_search_questions_empty_result(self):
        """測試搜尋題目無結果"""
        token = "test_token"
        search_params = {
            "subject": "不存在的科目",
            "grade": "7A"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬無搜尋結果
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "questions": [],
                "total": 0,
                "page": 1,
                "limit": 10
            }
            mock_request.return_value = mock_response
            
            result = self.question_client.search_questions(search_params, token)
            
            assert result["questions"] == []
            assert result["total"] == 0
    
    def test_invalid_token_access(self, test_question_data):
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
                self.question_client.create_question(test_question_data, invalid_token)
    
    @pytest.mark.parametrize("invalid_question_data", [
        {"question": ""},  # 空題目
        {"question": "test", "grade": "invalid_grade"},  # 無效年級
        {"question": "test", "subject": ""},  # 空科目
        {}  # 空資料
    ])
    def test_create_question_invalid_data(self, invalid_question_data):
        """測試創建題目無效資料"""
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
                self.question_client.create_question(invalid_question_data, token)

@pytest.mark.unit
class TestQuestionBankIntegration:
    """題庫服務整合測試"""
    
    def setup_method(self):
        """測試前設定"""
        self.question_client = QuestionBankClient()
    
    def test_question_lifecycle(self, test_question_data):
        """測試題目完整生命週期"""
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬創建成功
            create_response = Mock()
            create_response.status_code = 201
            create_response.json.return_value = {
                "id": "q123",
                "question": test_question_data["question"]
            }
            
            # 模擬獲取成功
            get_response = Mock()
            get_response.status_code = 200
            get_response.json.return_value = {
                "id": "q123",
                "question": test_question_data["question"]
            }
            
            # 模擬更新成功
            update_response = Mock()
            update_response.status_code = 200
            update_response.json.return_value = {
                "id": "q123",
                "question": "更新後的題目"
            }
            
            # 模擬刪除成功
            delete_response = Mock()
            delete_response.status_code = 204
            
            mock_request.side_effect = [create_response, get_response, update_response, delete_response]
            
            # 執行完整生命週期
            # 1. 創建題目
            create_result = self.question_client.create_question(test_question_data, token)
            assert create_result["id"] == "q123"
            
            # 2. 獲取題目
            get_result = self.question_client.get_question("q123", token)
            assert get_result["id"] == "q123"
            
            # 3. 更新題目
            update_result = self.question_client.update_question("q123", {"question": "更新後的題目"}, token)
            assert update_result["question"] == "更新後的題目"
            
            # 4. 刪除題目
            delete_result = self.question_client.delete_question("q123", token)
            assert delete_result == True 