#!/usr/bin/env python3
"""
API 端點測試腳本
使用 FastAPI TestClient 測試 API 功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

def create_mock_db():
    """創建模擬資料庫會話"""
    mock_db = MagicMock(spec=Session)
    return mock_db

def test_health_endpoint():
    """測試健康檢查端點"""
    print("🏥 測試健康檢查端點...")
    
    try:
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 健康檢查端點正常")
            return True
        else:
            print("❌ 健康檢查端點異常")
            return False
            
    except Exception as e:
        print(f"❌ 健康檢查測試失敗: {e}")
        return False

def test_root_endpoint():
    """測試根端點"""
    print("\n🏠 測試根端點...")
    
    try:
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/")
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 根端點正常")
            return True
        else:
            print("❌ 根端點異常")
            return False
            
    except Exception as e:
        print(f"❌ 根端點測試失敗: {e}")
        return False

def test_register_endpoint():
    """測試註冊端點"""
    print("\n📝 測試用戶註冊端點...")
    
    try:
        from app.main import app
        client = TestClient(app)
        
        # 測試資料
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "student",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # 模擬資料庫操作
        with patch('app.api.auth.get_db') as mock_get_db:
            mock_db = create_mock_db()
            mock_get_db.return_value = mock_db
            
            # 模擬用戶創建成功
            with patch('app.crud.create_user') as mock_create_user:
                mock_user = MagicMock()
                mock_user.id = 1
                mock_user.email = user_data["email"]
                mock_create_user.return_value = mock_user
                
                response = client.post("/api/v1/auth/register", json=user_data)
                print(f"狀態碼: {response.status_code}")
                print(f"回應內容: {response.json()}")
                
                if response.status_code == 201:
                    print("✅ 註冊端點正常")
                    return True
                else:
                    print("❌ 註冊端點異常")
                    return False
                    
    except Exception as e:
        print(f"❌ 註冊端點測試失敗: {e}")
        return False

def test_login_endpoint():
    """測試登入端點"""
    print("\n🔑 測試用戶登入端點...")
    
    try:
        from app.main import app
        client = TestClient(app)
        
        # 測試資料
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # 模擬資料庫操作
        with patch('app.api.auth.get_db') as mock_get_db:
            mock_db = create_mock_db()
            mock_get_db.return_value = mock_db
            
            # 模擬用戶認證成功
            with patch('app.crud.authenticate_user') as mock_auth:
                mock_user = MagicMock()
                mock_user.id = 1
                mock_user.email = login_data["email"]
                mock_user.role.value = "student"
                mock_user.is_active = True
                mock_auth.return_value = mock_user
                
                # 模擬 refresh token 創建
                with patch('app.crud.create_refresh_token') as mock_refresh:
                    mock_refresh.return_value = MagicMock()
                    
                    response = client.post("/api/v1/auth/login", json=login_data)
                    print(f"狀態碼: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        print(f"回應包含 access_token: {'access_token' in response_data}")
                        print(f"回應包含 refresh_token: {'refresh_token' in response_data}")
                        print("✅ 登入端點正常")
                        return True
                    else:
                        print(f"❌ 登入端點異常: {response.json()}")
                        return False
                        
    except Exception as e:
        print(f"❌ 登入端點測試失敗: {e}")
        return False

def test_api_documentation():
    """測試 API 文檔端點"""
    print("\n📚 測試 API 文檔端點...")
    
    try:
        from app.main import app
        client = TestClient(app)
        
        # 測試 Swagger UI
        response = client.get("/docs")
        print(f"Swagger UI 狀態碼: {response.status_code}")
        
        # 測試 ReDoc
        response = client.get("/redoc")
        print(f"ReDoc 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 文檔端點正常")
            return True
        else:
            print("❌ API 文檔端點異常")
            return False
            
    except Exception as e:
        print(f"❌ API 文檔測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 InULearning Auth Service API 測試")
    print("=" * 50)
    
    tests = [
        ("健康檢查端點", test_health_endpoint),
        ("根端點", test_root_endpoint),
        ("用戶註冊端點", test_register_endpoint),
        ("用戶登入端點", test_login_endpoint),
        ("API 文檔端點", test_api_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 API 測試結果總結:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項 API 測試通過")
    
    if passed == len(results):
        print("🎉 所有 API 測試通過！auth-service API 功能正常")
        return True
    else:
        print("⚠️  部分 API 測試失敗，需要檢查相關端點")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 