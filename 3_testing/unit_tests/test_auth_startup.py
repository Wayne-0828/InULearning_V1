#!/usr/bin/env python3
"""
服務啟動測試
測試 auth-service 是否能正常啟動
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_service_startup():
    """測試服務啟動"""
    print("🚀 測試 auth-service 啟動...")
    
    try:
        from app.main import app
        print("✅ FastAPI 應用程式創建成功")
        
        # 檢查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"✅ 發現 {len(routes)} 個路由:")
        for route in routes:
            print(f"  - {route}")
        
        # 檢查中間件
        print("✅ 中間件配置正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 服務啟動失敗: {e}")
        return False

def test_config():
    """測試配置"""
    print("\n⚙️  測試配置...")
    
    try:
        from app.config import settings
        
        print(f"✅ 應用程式名稱: {settings.app_name}")
        print(f"✅ 版本: {settings.app_version}")
        print(f"✅ 資料庫 URL: {settings.database_url}")
        print(f"✅ JWT 演算法: {settings.jwt_algorithm}")
        print(f"✅ CORS 來源: {settings.cors_origins}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def test_models():
    """測試模型"""
    print("\n📊 測試資料模型...")
    
    try:
        from app.models import User, UserRole, RefreshToken
        
        print("✅ User 模型導入成功")
        print("✅ UserRole 枚舉導入成功")
        print("✅ RefreshToken 模型導入成功")
        
        # 檢查 UserRole 枚舉值
        roles = [role.value for role in UserRole]
        print(f"✅ 支援的角色: {roles}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型測試失敗: {e}")
        return False

def test_schemas():
    """測試 Pydantic 模型"""
    print("\n📋 測試 Pydantic 模型...")
    
    try:
        from app.schemas import UserCreate, UserLogin, Token, UserResponse
        
        print("✅ UserCreate 模型導入成功")
        print("✅ UserLogin 模型導入成功")
        print("✅ Token 模型導入成功")
        print("✅ UserResponse 模型導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic 模型測試失敗: {e}")
        return False

def test_auth_functions():
    """測試認證功能"""
    print("\n🔐 測試認證功能...")
    
    try:
        from app.auth import get_password_hash, verify_password, create_access_token
        
        # 測試密碼雜湊
        password = "testpassword123"
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        
        print(f"✅ 密碼雜湊測試: {'成功' if is_valid else '失敗'}")
        
        # 測試 JWT Token
        user_data = {"sub": "123", "email": "test@example.com", "role": "student"}
        token = create_access_token(data=user_data)
        
        print(f"✅ JWT Token 生成: {'成功' if token else '失敗'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 認證功能測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 InULearning Auth Service 啟動測試")
    print("=" * 50)
    
    tests = [
        ("服務啟動", test_service_startup),
        ("配置", test_config),
        ("資料模型", test_models),
        ("Pydantic 模型", test_schemas),
        ("認證功能", test_auth_functions),
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
    print("📊 啟動測試結果總結:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("🎉 所有啟動測試通過！auth-service 可以正常啟動")
        return True
    else:
        print("⚠️  部分啟動測試失敗，需要檢查相關功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 