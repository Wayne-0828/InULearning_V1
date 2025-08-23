#!/usr/bin/env python3
"""
簡化的 Gemini API 整合測試

此腳本直接測試 Gemini API 功能，不依賴完整的 AI 分析服務
"""

import os
import sys
import json
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_api_integration():
    """測試 Gemini API 整合"""
    print("=== Gemini API 整合測試 ===")
    
    try:
        from gemini_api import student_learning_evaluation, solution_guidance
        
        # 測試題目資料
        question = {
            "grade": "7A",
            "subject": "數學",
            "publisher": "翰林",
            "chapter": "1-1正數與負數",
            "topic": "正數與負數",
            "knowledge_point": [
                "正負數的定義",
                "數線表示"
            ],
            "difficulty": "easy",
            "question": "下列關於正數與負數的敘述，何者正確？",
            "options": {
                "A": "$0$ 是正數。",
                "B": "$0$ 是負數。",
                "C": "$0$ 既不是正數也不是負數。",
                "D": "$0$ 是最小的正數。"
            },
            "answer": "C",
            "explanation": "$0$ 既不是正數也不是負數，它是正負數的分界點。"
        }

        student_answer = "B"
        
        print("1. 測試學生學習狀況評估...")
        evaluation_result = student_learning_evaluation(question, student_answer)
        print("✅ 學生學習狀況評估測試成功")
        print(f"結果: {evaluation_result['學生學習狀況評估'][:200]}...")
        
        print("\n2. 測試題目詳解與教學建議...")
        guidance_result = solution_guidance(question, student_answer)
        print("✅ 題目詳解與教學建議測試成功")
        print(f"結果: {guidance_result['題目詳解與教學建議'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API 整合測試失敗: {e}")
        return False

def test_environment_setup():
    """測試環境設定"""
    print("=== 環境設定測試 ===")
    
    # 檢查 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定")
        return False
    
    if api_key == "AIzaSyAl3lsmyeNvvI_0D08Ugftl6ZYEs4kX5MI":
        print("✅ GEMINI_API_KEY 已正確設定")
    else:
        print("⚠️ GEMINI_API_KEY 已設定，但與預期值不同")
    
    # 檢查必要套件
    try:
        import google.generativeai
        print("✅ google-generativeai 套件已安裝")
    except ImportError:
        print("❌ google-generativeai 套件未安裝")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv 套件已安裝")
    except ImportError:
        print("❌ python-dotenv 套件未安裝")
        return False
    
    return True

def test_frontend_integration():
    """測試前端整合準備"""
    print("=== 前端整合準備測試 ===")
    
    # 檢查前端檔案是否存在
    frontend_files = [
        "2_implementation/frontend/student-app/js/api/ai-analysis.js",
        "2_implementation/frontend/student-app/js/pages/result.js",
        "2_implementation/frontend/student-app/pages/result.html"
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            return False
    
    # 檢查後端路由檔案
    backend_files = [
        "2_implementation/backend/ai-analysis-service/src/routers/weakness_analysis.py",
        "2_implementation/backend/ai-analysis-service/src/routers/learning_recommendation.py"
    ]
    
    for file_path in backend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            return False
    
    return True

def generate_test_report():
    """生成測試報告"""
    print("\n=== 整合測試報告 ===")
    
    # 測試環境
    env_ok = test_environment_setup()
    
    # 測試 API 整合
    api_ok = test_gemini_api_integration()
    
    # 測試前端整合
    frontend_ok = test_frontend_integration()
    
    print("\n=== 測試結果總結 ===")
    print(f"環境設定: {'✅ 通過' if env_ok else '❌ 失敗'}")
    print(f"API 整合: {'✅ 通過' if api_ok else '❌ 失敗'}")
    print(f"前端整合: {'✅ 通過' if frontend_ok else '❌ 失敗'}")
    
    if env_ok and api_ok and frontend_ok:
        print("\n🎉 所有測試通過！Gemini API 整合成功")
        print("\n=== 下一步操作 ===")
        print("1. 啟動 AI 分析服務: cd 2_implementation/backend/ai-analysis-service && python run.py")
        print("2. 啟動前端服務: 開啟 2_implementation/frontend/student-app/pages/result.html")
        print("3. 測試完整功能: 進行練習並查看 AI 分析結果")
        return True
    else:
        print("\n⚠️ 部分測試失敗，請檢查相關設定")
        return False

if __name__ == "__main__":
    print("🚀 開始簡化 Gemini API 整合測試\n")
    success = generate_test_report()
    sys.exit(0 if success else 1)
