#!/usr/bin/env python3
"""
Question Bank Service 基本測試腳本
測試模組導入、模型定義和基本功能
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """測試模組導入"""
    print("🔍 測試模組導入...")
    
    try:
        from app.config import settings
        print("✅ 配置模組導入成功")
        
        from app.schemas import QuestionCreate, GradeEnum, SubjectEnum, PublisherEnum
        print("✅ 模型模組導入成功")
        
        from app.database import DatabaseManager
        print("✅ 資料庫模組導入成功")
        
        from app.crud import QuestionCRUD, ChapterCRUD, KnowledgePointCRUD
        print("✅ CRUD 模組導入成功")
        
        from app.main import app
        print("✅ 主應用程式模組導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")
        return False


def test_schemas():
    """測試模型定義"""
    print("\n🔍 測試模型定義...")
    
    try:
        from app.schemas import QuestionCreate, GradeEnum, SubjectEnum, PublisherEnum, DifficultyEnum
        
        # 測試枚舉值
        assert GradeEnum.GRADE_7A == "7A"
        assert SubjectEnum.MATH == "數學"
        assert PublisherEnum.NANI == "南一"
        assert DifficultyEnum.NORMAL == "normal"
        print("✅ 枚舉定義正確")
        
        # 測試題目模型
        question_data = {
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "chapter": "1-1 一元一次方程式",
            "topic": "一元一次方程式",
            "knowledge_point": ["方程式求解"],
            "difficulty": "normal",
            "question": "解下列方程式：2x + 5 = 13",
            "options": {
                "A": "x = 4",
                "B": "x = 6",
                "C": "x = 8",
                "D": "x = 10"
            },
            "answer": "A",
            "explanation": "解一元一次方程式 2x + 5 = 13，首先將 5 移到等式右邊得到 2x = 13 - 5 = 8，再將兩邊同除以 2 得到 x = 4，因此正確答案是選項 A。"
        }
        
        question = QuestionCreate(**question_data)
        assert question.grade == GradeEnum.GRADE_7A
        assert question.subject == SubjectEnum.MATH
        assert question.publisher == PublisherEnum.NANI
        assert question.difficulty == DifficultyEnum.NORMAL
        print("✅ 題目模型創建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型定義測試失敗: {e}")
        return False


def test_fastapi_app():
    """測試 FastAPI 應用程式"""
    print("\n🔍 測試 FastAPI 應用程式...")
    
    try:
        from app.main import app
        
        # 檢查應用程式屬性
        assert app.title == "InULearning Question Bank Service"
        assert app.version == "1.0.0"
        print("✅ FastAPI 應用程式創建成功")
        
        # 檢查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"✅ 發現 {len(routes)} 個路由:")
        for route in routes:
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI 應用程式測試失敗: {e}")
        return False


def test_config():
    """測試配置設定"""
    print("\n🔍 測試配置設定...")
    
    try:
        from app.config import settings
        
        # 檢查基本配置
        assert settings.app_name == "InULearning Question Bank Service"
        assert settings.app_version == "1.0.0"
        assert settings.mongodb_database == "inulearning_question_bank"
        assert settings.api_prefix == "/api/v1"
        print("✅ 配置設定正確")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置設定測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 Question Bank Service 基本測試開始")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_schemas,
        test_fastapi_app,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有基本測試通過！")
        return True
    else:
        print("⚠️  部分測試失敗，請檢查錯誤訊息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 