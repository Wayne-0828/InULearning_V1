"""
API 客戶端模組
提供各個微服務的 API 測試客戶端
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from .test_helpers import TestResult, List
from .test_helpers import APITestHelper

class BaseAPIClient:
    """基礎 API 客戶端"""
    
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.session = requests.Session()
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        
        # 設定預設 headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"{method} {url} -> {response.status_code}")
            return response
        except Exception as e:
            self.logger.error(f"請求失敗: {method} {url} - {e}")
            raise
    
    def _validate_response(self, response: requests.Response, expected_status: int = 200) -> TestResult:
        """驗證回應並返回 TestResult"""
        try:
            if response.status_code != expected_status:
                return TestResult(
                    success=False, 
                    message=f"{self.service_name} API 回應狀態碼錯誤", 
                    error=f"狀態碼: {response.status_code}, 預期: {expected_status}"
                )
            
            data = response.json()
            return TestResult(success=True, message="API 請求成功", data=data)
        except json.JSONDecodeError:
            return TestResult(
                success=False, 
                message=f"{self.service_name} API 回應格式錯誤", 
                error="回應不是有效的 JSON 格式"
            )
        except Exception as e:
            return TestResult(
                success=False, 
                message=f"{self.service_name} API 請求失敗", 
                error=str(e)
            )
    
    def health_check(self) -> bool:
        """健康檢查"""
        try:
            response = self._make_request('GET', '/health')
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"健康檢查失敗: {e}")
            return False
    
    def get_docs(self) -> Optional[str]:
        """獲取 API 文檔"""
        try:
            response = self._make_request('GET', '/docs')
            return response.text if response.status_code == 200 else None
        except Exception as e:
            self.logger.error(f"獲取文檔失敗: {e}")
            return None
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """發送 GET 請求"""
        return self._make_request('GET', endpoint, **kwargs)

class AuthServiceClient(BaseAPIClient):
    """認證服務 API 客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        super().__init__(base_url, "auth-service")
    
    def register_user(self, user_data: Dict[str, Any]) -> TestResult:
        """註冊用戶"""
        try:
            response = self._make_request('POST', '/api/v1/auth/register', json=user_data)
            return self._validate_response(response, 201)
        except Exception as e:
            return TestResult(success=False, message="用戶註冊失敗", error=str(e))
    
    def login_user(self, credentials: Dict[str, str]) -> TestResult:
        """用戶登入"""
        try:
            response = self._make_request('POST', '/api/v1/auth/login', json=credentials)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="用戶登入失敗", error=str(e))
    
    def get_user_profile(self, user_id: str) -> TestResult:
        """獲取用戶資料"""
        try:
            response = self._make_request('GET', f'/api/v1/users/{user_id}/profile')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取用戶資料失敗", error=str(e))
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> TestResult:
        """更新用戶資料"""
        try:
            response = self._make_request('PUT', f'/api/v1/users/{user_id}/profile', json=profile_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="更新用戶資料失敗", error=str(e))
    
    def refresh_token(self, refresh_token: str) -> TestResult:
        """刷新 token"""
        try:
            data = {'refresh_token': refresh_token}
            response = self._make_request('POST', '/api/v1/auth/refresh', json=data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="刷新 token 失敗", error=str(e))
    
    def logout_user(self, token: str) -> TestResult:
        """用戶登出"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = self._make_request('POST', '/api/v1/auth/logout', headers=headers)
            return TestResult(success=response.status_code == 200, message="用戶登出")
        except Exception as e:
            return TestResult(success=False, message="用戶登出失敗", error=str(e))

class LearningServiceClient(BaseAPIClient):
    """學習服務 API 客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        super().__init__(base_url, "learning-service")
    
    def create_exercise_session(self, session_data: Dict[str, Any]) -> TestResult:
        """創建練習會話"""
        try:
            response = self._make_request('POST', '/api/v1/sessions', json=session_data)
            return self._validate_response(response, 201)
        except Exception as e:
            return TestResult(success=False, message="創建練習會話失敗", error=str(e))
    
    def get_learning_session(self, session_id: str) -> TestResult:
        """獲取學習會話"""
        try:
            response = self._make_request('GET', f'/api/v1/sessions/{session_id}')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取學習會話失敗", error=str(e))
    
    def submit_answer(self, session_id: str, answer_data: Dict[str, Any]) -> TestResult:
        """提交答案"""
        try:
            response = self._make_request('POST', f'/api/v1/sessions/{session_id}/answers', json=answer_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="提交答案失敗", error=str(e))
    
    def get_session_progress(self, session_id: str) -> TestResult:
        """獲取會話進度"""
        try:
            response = self._make_request('GET', f'/api/v1/sessions/{session_id}/progress')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取會話進度失敗", error=str(e))
    
    def complete_session(self, session_id: str) -> TestResult:
        """完成學習會話"""
        try:
            response = self._make_request('POST', f'/api/v1/sessions/{session_id}/complete')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="完成學習會話失敗", error=str(e))
    
    def get_learning_recommendations(self, user_id: str) -> TestResult:
        """獲取學習建議"""
        try:
            response = self._make_request('GET', f'/api/v1/users/{user_id}/recommendations')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取學習建議失敗", error=str(e))
    
    def get_learning_trends(self, user_id: str) -> TestResult:
        """獲取學習趨勢"""
        try:
            response = self._make_request('GET', f'/api/v1/users/{user_id}/trends')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取學習趨勢失敗", error=str(e))

class QuestionBankClient(BaseAPIClient):
    """題庫服務 API 客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        super().__init__(base_url, "question-bank-service")
    
    def create_question(self, question_data: Dict[str, Any]) -> TestResult:
        """創建題目"""
        try:
            response = self._make_request('POST', '/api/v1/questions', json=question_data)
            return self._validate_response(response, 201)
        except Exception as e:
            return TestResult(success=False, message="創建題目失敗", error=str(e))
    
    def get_question(self, question_id: str) -> TestResult:
        """獲取題目"""
        try:
            response = self._make_request('GET', f'/api/v1/questions/{question_id}')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取題目失敗", error=str(e))
    
    def update_question(self, question_id: str, question_data: Dict[str, Any]) -> TestResult:
        """更新題目"""
        try:
            response = self._make_request('PUT', f'/api/v1/questions/{question_id}', json=question_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="更新題目失敗", error=str(e))
    
    def delete_question(self, question_id: str) -> TestResult:
        """刪除題目"""
        try:
            response = self._make_request('DELETE', f'/api/v1/questions/{question_id}')
            return TestResult(success=response.status_code == 204, message="刪除題目")
        except Exception as e:
            return TestResult(success=False, message="刪除題目失敗", error=str(e))
    
    def search_questions(self, search_params: Dict[str, Any]) -> TestResult:
        """搜尋題目"""
        try:
            response = self._make_request('GET', '/api/v1/questions/search', params=search_params)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="搜尋題目失敗", error=str(e))
    
    def get_random_questions(self, params: Dict[str, Any]) -> TestResult:
        """獲取隨機題目"""
        try:
            response = self._make_request('GET', '/api/v1/questions/random', params=params)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取隨機題目失敗", error=str(e))
    
    def get_chapters(self, subject: str, grade: str) -> TestResult:
        """獲取章節列表"""
        try:
            params = {'subject': subject, 'grade': grade}
            response = self._make_request('GET', '/api/v1/chapters', params=params)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取章節列表失敗", error=str(e))
    
    def get_knowledge_points(self, chapter_id: str) -> TestResult:
        """獲取知識點"""
        try:
            response = self._make_request('GET', f'/api/v1/chapters/{chapter_id}/knowledge-points')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="獲取知識點失敗", error=str(e))

class AIAnalysisClient(BaseAPIClient):
    """AI 分析服務 API 客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        super().__init__(base_url, "ai-analysis-service")
    
    def analyze_weaknesses(self, session_data: Dict[str, Any]) -> TestResult:
        """分析學習弱點"""
        try:
            response = self._make_request('POST', '/api/v1/analysis/weaknesses', json=session_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="弱點分析失敗", error=str(e))
    
    def get_learning_recommendations(self, user_data: Dict[str, Any]) -> TestResult:
        """獲取學習建議"""
        try:
            response = self._make_request('POST', '/api/v1/analysis/recommendations', json=user_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="學習建議失敗", error=str(e))
    
    def get_trend_analysis(self, user_id: str) -> TestResult:
        """獲取趨勢分析"""
        try:
            response = self._make_request('GET', f'/api/v1/analysis/trends/{user_id}')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="趨勢分析失敗", error=str(e))
    
    def generate_report(self, user_id: str, report_type: str) -> TestResult:
        """生成報告"""
        try:
            data = {'user_id': user_id, 'report_type': report_type}
            response = self._make_request('POST', '/api/v1/analysis/reports', json=data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="報告生成失敗", error=str(e))
    
    def get_ai_insights(self, user_id: str) -> TestResult:
        """獲取 AI 洞察"""
        try:
            response = self._make_request('GET', f'/api/v1/analysis/insights/{user_id}')
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="AI 洞察失敗", error=str(e))
    
    def generate_question_embedding(self, question_data: Dict[str, Any]) -> TestResult:
        """生成題目向量嵌入"""
        try:
            response = self._make_request('POST', '/api/v1/vectors/embeddings', json=question_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="向量嵌入生成失敗", error=str(e))
    
    def search_similar_questions(self, search_data: Dict[str, Any]) -> TestResult:
        """搜尋相似題目"""
        try:
            response = self._make_request('POST', '/api/v1/vectors/search', json=search_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="相似題目搜尋失敗", error=str(e))
    
    def update_question_embedding(self, update_data: Dict[str, Any]) -> TestResult:
        """更新題目向量嵌入"""
        try:
            response = self._make_request('PUT', '/api/v1/vectors/embeddings', json=update_data)
            return self._validate_response(response, 200)
        except Exception as e:
            return TestResult(success=False, message="向量嵌入更新失敗", error=str(e))

# 全域 API 客戶端實例
auth_client = AuthServiceClient()
learning_client = LearningServiceClient()
question_bank_client = QuestionBankClient()
ai_analysis_client = AIAnalysisClient() 