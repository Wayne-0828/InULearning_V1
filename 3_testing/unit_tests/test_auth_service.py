"""
認證服務單元測試
測試用戶註冊、登入、認證等功能
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from utils.api_client import AuthServiceClient
from utils.test_helpers import TestHelper

@pytest.mark.unit
class TestAuthService:
    """認證服務測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.auth_client = AuthServiceClient()
        self.test_helper = TestHelper()
    
    def test_health_check(self):
        """測試健康檢查端點"""
        assert self.auth_client.health_check() == True
    
    def test_register_user_success(self, test_user_data):
        """測試用戶註冊成功"""
        with patch('requests.Session.request') as mock_request:
            # 模擬成功回應
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "id": 1,
                "email": test_user_data["email"],
                "username": test_user_data["username"],
                "message": "用戶註冊成功"
            }
            mock_request.return_value = mock_response
            
            result = self.auth_client.register_user(test_user_data)
            
            assert result["id"] == 1
            assert result["email"] == test_user_data["email"]
            assert result["username"] == test_user_data["username"]
    
    def test_register_user_duplicate_email(self, test_user_data):
        """測試重複郵件註冊"""
        with patch('requests.Session.request') as mock_request:
            # 模擬重複郵件錯誤
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "detail": "郵件地址已存在"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.auth_client.register_user(test_user_data)
    
    def test_login_user_success(self, test_user_data):
        """測試用戶登入成功"""
        credentials = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功登入
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": test_user_data["email"],
                    "username": test_user_data["username"]
                }
            }
            mock_request.return_value = mock_response
            
            result = self.auth_client.login_user(credentials)
            
            assert "access_token" in result
            assert "refresh_token" in result
            assert result["token_type"] == "bearer"
            assert result["user"]["email"] == test_user_data["email"]
    
    def test_login_user_invalid_credentials(self, test_user_data):
        """測試無效憑證登入"""
        credentials = {
            "email": test_user_data["email"],
            "password": "wrong_password"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬認證失敗
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "detail": "無效的郵件或密碼"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.auth_client.login_user(credentials)
    
    def test_get_user_profile(self, test_user_data):
        """測試獲取用戶資料"""
        user_id = 1
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功獲取資料
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": user_id,
                "email": test_user_data["email"],
                "username": test_user_data["username"],
                "first_name": test_user_data["first_name"],
                "last_name": test_user_data["last_name"],
                "role": test_user_data["role"]
            }
            mock_request.return_value = mock_response
            
            result = self.auth_client.get_user_profile(user_id, token)
            
            assert result["id"] == user_id
            assert result["email"] == test_user_data["email"]
            assert result["username"] == test_user_data["username"]
    
    def test_update_user_profile(self, test_user_data):
        """測試更新用戶資料"""
        user_id = 1
        token = "test_token"
        profile_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功更新
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": user_id,
                "first_name": "Updated",
                "last_name": "Name",
                "message": "資料更新成功"
            }
            mock_request.return_value = mock_response
            
            result = self.auth_client.update_user_profile(user_id, profile_data, token)
            
            assert result["first_name"] == "Updated"
            assert result["last_name"] == "Name"
    
    def test_refresh_token(self):
        """測試刷新 token"""
        refresh_token = "test_refresh_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功刷新
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "bearer"
            }
            mock_request.return_value = mock_response
            
            result = self.auth_client.refresh_token(refresh_token)
            
            assert "access_token" in result
            assert "refresh_token" in result
            assert result["token_type"] == "bearer"
    
    def test_logout_user(self):
        """測試用戶登出"""
        token = "test_token"
        
        with patch('requests.Session.request') as mock_request:
            # 模擬成功登出
            mock_response = Mock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response
            
            result = self.auth_client.logout_user(token)
            
            assert result == True
    
    def test_invalid_token_access(self, test_user_data):
        """測試無效 token 存取"""
        user_id = 1
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
                self.auth_client.get_user_profile(user_id, invalid_token)
    
    @pytest.mark.parametrize("invalid_data", [
        {"email": "invalid-email"},  # 無效郵件格式
        {"email": "test@example.com", "password": ""},  # 空密碼
        {"email": "", "password": "testpass"},  # 空郵件
        {}  # 空資料
    ])
    def test_register_user_invalid_data(self, invalid_data):
        """測試無效資料註冊"""
        with patch('requests.Session.request') as mock_request:
            # 模擬驗證錯誤
            mock_response = Mock()
            mock_response.status_code = 422
            mock_response.json.return_value = {
                "detail": "資料驗證失敗"
            }
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 回應狀態碼錯誤"):
                self.auth_client.register_user(invalid_data)
    
    def test_service_unavailable(self, test_user_data):
        """測試服務不可用"""
        with patch('requests.Session.request') as mock_request:
            # 模擬服務不可用
            mock_request.side_effect = Exception("Connection refused")
            
            with pytest.raises(Exception, match="Connection refused"):
                self.auth_client.register_user(test_user_data)

@pytest.mark.unit
class TestAuthServiceIntegration:
    """認證服務整合測試"""
    
    def setup_method(self):
        """測試前設定"""
        self.auth_client = AuthServiceClient()
    
    def test_complete_auth_flow(self, test_user_data):
        """測試完整認證流程"""
        # 1. 註冊用戶
        with patch('requests.Session.request') as mock_request:
            # 模擬註冊成功
            register_response = Mock()
            register_response.status_code = 201
            register_response.json.return_value = {
                "id": 1,
                "email": test_user_data["email"],
                "username": test_user_data["username"]
            }
            
            # 模擬登入成功
            login_response = Mock()
            login_response.status_code = 200
            login_response.json.return_value = {
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "user": {"id": 1, "email": test_user_data["email"]}
            }
            
            # 模擬獲取資料成功
            profile_response = Mock()
            profile_response.status_code = 200
            profile_response.json.return_value = {
                "id": 1,
                "email": test_user_data["email"],
                "username": test_user_data["username"]
            }
            
            mock_request.side_effect = [register_response, login_response, profile_response]
            
            # 執行完整流程
            register_result = self.auth_client.register_user(test_user_data)
            assert register_result["id"] == 1
            
            login_result = self.auth_client.login_user({
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            assert "access_token" in login_result
            
            profile_result = self.auth_client.get_user_profile(1, login_result["access_token"])
            assert profile_result["email"] == test_user_data["email"] 