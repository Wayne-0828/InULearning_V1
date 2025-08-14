#!/usr/bin/env python3
"""
Gemini API 整合測試腳本

此腳本用於測試 Gemini API 與 InULearning 系統的整合
"""

import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_api():
    """測試 Gemini API 基本功能"""
    print("=== 測試 Gemini API 基本功能 ===")
    
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
        print(f"結果: {evaluation_result['學生學習狀況評估'][:100]}...")
        
        print("\n2. 測試題目詳解與教學建議...")
        guidance_result = solution_guidance(question, student_answer)
        print("✅ 題目詳解與教學建議測試成功")
        print(f"結果: {guidance_result['題目詳解與教學建議'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API 測試失敗: {e}")
        return False

def test_environment():
    """測試環境設定"""
    print("=== 測試環境設定 ===")
    
    # 檢查 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定")
        return False
    
    if api_key == "AIzaSyAl3lsmyeNvvI_0D08Ugftl6ZYEs4kX5MI":
        print("✅ GEMINI_API_KEY 已設定")
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

def test_api_endpoints():
    """測試 API 端點（需要 AI 分析服務運行）"""
    print("=== 測試 API 端點 ===")
    
    try:
        import httpx
        
        # 測試健康檢查
        response = httpx.get("http://localhost:8004/health", timeout=5.0)
        if response.status_code == 200:
            print("✅ AI 分析服務健康檢查通過")
        else:
            print(f"❌ AI 分析服務健康檢查失敗: {response.status_code}")
            return False
        
        # 測試弱點分析端點
        question = {
            "grade": "7A",
            "subject": "數學",
            "publisher": "翰林",
            "chapter": "1-1正數與負數",
            "topic": "正數與負數",
            "knowledge_point": ["正負數的定義"],
            "difficulty": "easy",
            "question": "下列關於正數與負數的敘述，何者正確？",
            "options": {"A": "0是正數", "B": "0是負數", "C": "0既不是正數也不是負數", "D": "0是最小的正數"},
            "answer": "C",
            "explanation": "0既不是正數也不是負數"
        }
        
        response = httpx.post(
            "http://localhost:8004/api/v1/weakness-analysis/question-analysis",
            json={
                "question": question,
                "student_answer": "B",
                "temperature": 1.0,
                "max_output_tokens": 512
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 弱點分析 API 端點測試成功")
            print(f"結果: {result.get('data', {}).get('學生學習狀況評估', '')[:100]}...")
        else:
            print(f"❌ 弱點分析 API 端點測試失敗: {response.status_code}")
            print(f"錯誤: {response.text}")
            return False
        
        # 測試學習建議端點
        response = httpx.post(
            "http://localhost:8004/api/v1/learning-recommendation/question-guidance",
            json={
                "question": question,
                "student_answer": "B",
                "temperature": 1.0,
                "max_output_tokens": 512
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 學習建議 API 端點測試成功")
            print(f"結果: {result.get('data', {}).get('題目詳解與教學建議', '')[:100]}...")
        else:
            print(f"❌ 學習建議 API 端點測試失敗: {response.status_code}")
            print(f"錯誤: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API 端點測試失敗: {e}")
        print("請確保 AI 分析服務正在運行 (http://localhost:8004)")
        return False

def main():
    """主測試函數"""
    print("🚀 開始 Gemini API 整合測試\n")
    
    # 測試環境
    if not test_environment():
        print("\n❌ 環境測試失敗，請檢查設定")
        return False
    
    print()
    
    # 測試 Gemini API
    if not test_gemini_api():
        print("\n❌ Gemini API 測試失敗")
        return False
    
    print()
    
    # 測試 API 端點
    if not test_api_endpoints():
        print("\n⚠️ API 端點測試失敗，可能是服務未運行")
        print("請啟動 AI 分析服務後再測試")
        return False
    
    print("\n🎉 所有測試通過！Gemini API 整合成功")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
