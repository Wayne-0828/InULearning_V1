#!/usr/bin/env python3
"""
基本功能測試腳本
測試 auth-service 的核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """測試所有模組的導入"""
    print("🔍 測試模組導入...")
    
    try:
        from app.config import settings
        print("✅ config.py 導入成功")
    except Exception as e:
        print(f"❌ config.py 導入失敗: {e}")
        return False
    
    try:
        from app.models import User, UserRole, RefreshToken
        print("✅ models.py 導入成功")
    except Exception as e:
        print(f"❌ models.py 導入失敗: {e}")
        return False
    
    try:
        from app.schemas import UserCreate, UserLogin, Token
        print("✅ schemas.py 導入成功")
    except Exception as e:
        print(f"❌ schemas.py 導入失敗: {e}")
        return False
    
    try:
        from app.auth import verify_password, get_password_hash, create_access_token
        print("✅ auth.py 導入成功")
    except Exception as e:
        print(f"❌ auth.py 導入失敗: {e}")
        return False
    
    try:
        from app.crud import create_user, authenticate_user
        print("✅ crud.py 導入成功")
    except Exception as e:
        print(f"❌ crud.py 導入失敗: {e}")
        return False
    
    return True

def test_password_hashing():
    """測試密碼雜湊功能"""
    print("\n🔐 測試密碼雜湊功能...")
    
    try:
        from app.auth import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        print(f"原始密碼: {password}")
        print(f"雜湊密碼: {hashed[:20]}...")
        
        # 測試驗證
        is_valid = verify_password(password, hashed)
        print(f"密碼驗證: {'✅ 成功' if is_valid else '❌ 失敗'}")
        
        # 測試錯誤密碼
        is_invalid = verify_password("wrongpassword", hashed)
        print(f"錯誤密碼驗證: {'✅ 正確拒絕' if not is_invalid else '❌ 錯誤接受'}")
        
        return is_valid and not is_invalid
    except Exception as e:
        print(f"❌ 密碼雜湊測試失敗: {e}")
        return False

def test_jwt_token():
    """測試 JWT Token 功能"""
    print("\n🎫 測試 JWT Token 功能...")
    
    try:
        from app.auth import create_access_token, verify_token
        
        # 測試資料
        user_data = {
            "sub": "123",
            "email": "test@example.com",
            "role": "student"
        }
        
        # 建立 token
        token = create_access_token(data=user_data)
        print(f"生成的 Token: {token[:50]}...")
        
        # 驗證 token
        token_data = verify_token(token)
        if token_data:
            print(f"Token 驗證成功: user_id={token_data.user_id}, email={token_data.email}")
            return True
        else:
            print("❌ Token 驗證失敗")
            return False
            
    except Exception as e:
        print(f"❌ JWT Token 測試失敗: {e}")
        return False

def test_schemas():
    """測試 Pydantic 模型"""
    print("\n📋 測試 Pydantic 模型...")
    
    try:
        from app.schemas import UserCreate, UserLogin
        from app.models import UserRole
        
        # 測試用戶創建模型
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "student",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user_create = UserCreate(**user_data)
        print(f"✅ 用戶創建模型驗證成功: {user_create.email}")
        
        # 測試登入模型
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        user_login = UserLogin(**login_data)
        print(f"✅ 登入模型驗證成功: {user_login.email}")
        
        return True
    except Exception as e:
        print(f"❌ Pydantic 模型測試失敗: {e}")
        return False

def test_fastapi_app():
    """測試 FastAPI 應用程式"""
    print("\n🚀 測試 FastAPI 應用程式...")
    
    try:
        from app.main import app
        
        # 檢查路由
        routes = [route.path for route in app.routes]
        print(f"✅ FastAPI 應用程式啟動成功")
        print(f"發現 {len(routes)} 個路由:")
        for route in routes[:5]:  # 只顯示前5個
            print(f"  - {route}")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI 應用程式測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 InULearning Auth Service 功能測試")
    print("=" * 50)
    
    tests = [
        ("模組導入", test_imports),
        ("密碼雜湊", test_password_hashing),
        ("JWT Token", test_jwt_token),
        ("Pydantic 模型", test_schemas),
        ("FastAPI 應用程式", test_fastapi_app),
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
    print("📊 測試結果總結:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("🎉 所有測試通過！auth-service 基本功能正常")
        return True
    else:
        print("⚠️  部分測試失敗，需要檢查相關功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 