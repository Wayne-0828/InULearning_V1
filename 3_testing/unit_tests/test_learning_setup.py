#!/usr/bin/env python3
"""
測試設置腳本

用於驗證 learning-service 的開發環境和基本功能
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """測試模組導入"""
    print("🔍 測試模組導入...")
    
    try:
        from src.main import app
        print("✅ FastAPI 應用程式導入成功")
        
        from src.models.base import Base
        print("✅ 基礎模型導入成功")
        
        from src.models.learning_session import LearningSession, LearningRecord
        print("✅ 學習會話模型導入成功")
        
        from src.models.schemas import ExerciseParams, Answer
        print("✅ Pydantic 模型導入成功")
        
        from src.services.exercise_service import ExerciseService
        print("✅ 練習服務導入成功")
        
        from src.services.question_bank_client import QuestionBankClient
        print("✅ 題庫客戶端導入成功")
        
        from src.services.ai_analysis_client import AIAnalysisClient
        print("✅ AI 分析客戶端導入成功")
        
        from src.utils.database import get_db_session
        print("✅ 資料庫工具導入成功")
        
        from src.utils.auth import get_current_user
        print("✅ 認證工具導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False


def test_app_configuration():
    """測試應用程式配置"""
    print("\n🔍 測試應用程式配置...")
    
    try:
        from src.main import app
        
        # 檢查應用程式基本資訊
        assert app.title == "InULearning Learning Service"
        assert app.version == "v1.0.0"
        assert app.description is not None
        
        print("✅ 應用程式基本配置正確")
        
        # 檢查路由註冊
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/docs", "/redoc", "/openapi.json"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ 路由 {route} 已註冊")
            else:
                print(f"⚠️  路由 {route} 未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 應用程式配置測試失敗: {e}")
        return False


def test_environment_variables():
    """測試環境變數"""
    print("\n🔍 測試環境變數...")
    
    # 載入環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "PORT",
        "HOST"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value[:20]}..." if len(str(value)) > 20 else f"✅ {var} = {value}")
        else:
            print(f"⚠️  {var} 未設定")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  缺少環境變數: {', '.join(missing_vars)}")
        print("請複製 env.example 到 .env 並設定相應值")
        return False
    
    return True


async def test_database_connection():
    """測試資料庫連接"""
    print("\n🔍 測試資料庫連接...")
    
    try:
        from src.utils.database import engine
        
        # 測試連接
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ 資料庫連接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        print("請確保 PostgreSQL 服務正在運行且配置正確")
        return False


def test_service_initialization():
    """測試服務初始化"""
    print("\n🔍 測試服務初始化...")
    
    try:
        # 測試練習服務
        from src.services.exercise_service import ExerciseService
        exercise_service = ExerciseService()
        print("✅ 練習服務初始化成功")
        
        # 測試題庫客戶端
        from src.services.question_bank_client import QuestionBankClient
        question_client = QuestionBankClient()
        print("✅ 題庫客戶端初始化成功")
        
        # 測試 AI 分析客戶端
        from src.services.ai_analysis_client import AIAnalysisClient
        ai_client = AIAnalysisClient()
        print("✅ AI 分析客戶端初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服務初始化失敗: {e}")
        return False


async def test_basic_functionality():
    """測試基本功能"""
    print("\n🔍 測試基本功能...")
    
    try:
        # 測試 Pydantic 模型
        from src.models.schemas import ExerciseParams
        
        exercise_params = ExerciseParams(
            grade="7A",
            subject="數學",
            publisher="南一",
            chapter="第一章",
            difficulty="normal",
            question_count=5,
            knowledge_points=["基礎運算", "代數概念"]
        )
        
        print("✅ Pydantic 模型驗證成功")
        
        # 測試服務方法（不實際調用外部服務）
        from src.services.exercise_service import ExerciseService
        service = ExerciseService()
        
        # 測試預估時間計算
        questions = [{"question_id": f"q{i}"} for i in range(5)]
        estimated_time = service._calculate_estimated_time(questions)
        assert estimated_time == 10  # 5題 * 2分鐘
        
        print("✅ 基本業務邏輯測試成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能測試失敗: {e}")
        return False


async def main():
    """主函數"""
    print("🚀 InULearning Learning Service 開發環境測試")
    print("=" * 50)
    
    tests = [
        ("模組導入", test_imports),
        ("應用程式配置", test_app_configuration),
        ("環境變數", test_environment_variables),
        ("資料庫連接", test_database_connection),
        ("服務初始化", test_service_initialization),
        ("基本功能", test_basic_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！開發環境配置正確。")
        print("\n下一步:")
        print("1. 啟動服務: python run.py")
        print("2. 查看 API 文檔: http://localhost:8002/docs")
        print("3. 運行完整測試: pytest")
    else:
        print("⚠️  部分測試失敗，請檢查配置。")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 