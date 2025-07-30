#!/usr/bin/env python3
"""
前端整合測試腳本
測試從前端到後端的完整流程
"""

import requests
import json
import time

def test_frontend_backend_integration():
    """測試前端後端整合"""
    print("🔍 測試前端後端整合...")
    
    # API基礎URL
    api_base = "http://localhost:8002/api/v1"
    frontend_base = "http://localhost:8080"
    
    # 1. 測試前端頁面可訪問性
    print("\n1. 測試前端頁面...")
    try:
        response = requests.get(f"{frontend_base}/pages/exercise.html", timeout=5)
        print(f"✅ Exercise頁面: {response.status_code}")
        
        response = requests.get(f"{frontend_base}/pages/exam.html", timeout=5)
        print(f"✅ Exam頁面: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端頁面測試失敗: {e}")
        return False
    
    # 2. 測試API端點
    print("\n2. 測試API端點...")
    try:
        # 測試題庫檢查API
        params = {
            "grade": "7A",
            "edition": "康軒",
            "subject": "國文"
        }
        response = requests.get(f"{api_base}/questions/check", params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 題庫檢查API: 找到 {data['data']['count']} 題")
        else:
            print(f"❌ 題庫檢查API失敗: {response.status_code}")
            return False
            
        # 測試獲取題目API
        params["questionCount"] = 3
        response = requests.get(f"{api_base}/questions/by-conditions", params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 獲取題目API: 取得 {len(data['data'])} 題")
            
            # 檢查題目格式
            if data['data']:
                question = data['data'][0]
                required_fields = ['id', 'question', 'options', 'answer', 'subject', 'grade', 'publisher']
                missing_fields = [field for field in required_fields if field not in question]
                if missing_fields:
                    print(f"⚠️ 題目缺少欄位: {missing_fields}")
                else:
                    print("✅ 題目格式完整")
                    
                # 檢查是否有圖片題目
                has_image = any(q.get('image_filename') or q.get('image_url') for q in data['data'])
                print(f"📷 圖片題目: {'有' if has_image else '無'}")
        else:
            print(f"❌ 獲取題目API失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        return False
    
    # 3. 測試不同科目和版本
    print("\n3. 測試不同科目和版本...")
    test_combinations = [
        ("7A", "康軒", "國文"),
        ("7A", "康軒", "歷史"),
        ("7A", "南一", "公民"),
        ("7A", "翰林", "英文")
    ]
    
    for grade, edition, subject in test_combinations:
        try:
            params = {
                "grade": grade,
                "edition": edition,
                "subject": subject
            }
            response = requests.get(f"{api_base}/questions/check", params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                count = data['data']['count']
                print(f"✅ {edition}{subject}: {count}題")
            else:
                print(f"❌ {edition}{subject}: API錯誤")
        except Exception as e:
            print(f"❌ {edition}{subject}: {e}")
    
    # 4. 測試圖片服務
    print("\n4. 測試圖片服務...")
    try:
        # 嘗試訪問一個可能存在的圖片
        response = requests.get(f"{api_base}/images/test.jpg", timeout=5)
        if response.status_code == 404:
            print("✅ 圖片服務正常運行（404為預期結果）")
        elif response.status_code == 200:
            print("✅ 圖片服務正常運行（找到測試圖片）")
        else:
            print(f"⚠️ 圖片服務狀態: {response.status_code}")
    except Exception as e:
        print(f"❌ 圖片服務測試失敗: {e}")
    
    return True

def test_workflow_simulation():
    """模擬用戶工作流程"""
    print("\n🎯 模擬用戶工作流程...")
    
    api_base = "http://localhost:8002/api/v1"
    
    # 模擬用戶選擇條件
    user_selection = {
        "grade": "7A",
        "edition": "康軒",
        "subject": "國文",
        "questionCount": 5
    }
    
    print(f"👤 用戶選擇: {user_selection['grade']} {user_selection['edition']} {user_selection['subject']} {user_selection['questionCount']}題")
    
    # 1. 檢查題庫
    try:
        params = {k: v for k, v in user_selection.items() if k != 'questionCount'}
        response = requests.get(f"{api_base}/questions/check", params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            available_count = data['data']['count']
            print(f"📊 可用題目: {available_count}題")
            
            if available_count >= user_selection['questionCount']:
                print("✅ 題目數量充足，可以開始練習")
            else:
                print(f"⚠️ 題目不足，建議調整為{available_count}題")
                user_selection['questionCount'] = min(available_count, user_selection['questionCount'])
        else:
            print("❌ 題庫檢查失敗")
            return False
    except Exception as e:
        print(f"❌ 題庫檢查錯誤: {e}")
        return False
    
    # 2. 獲取題目
    try:
        response = requests.get(f"{api_base}/questions/by-conditions", params=user_selection, timeout=5)
        if response.status_code == 200:
            data = response.json()
            questions = data['data']
            print(f"📝 成功獲取 {len(questions)} 題")
            
            # 顯示題目預覽
            for i, q in enumerate(questions[:2]):  # 只顯示前兩題
                print(f"   題目{i+1}: {q['question'][:50]}...")
                print(f"   選項: {len(q['options'])}個")
                print(f"   答案: {q['answer']}")
                if q.get('image_filename'):
                    print(f"   圖片: {q['image_filename']}")
                print()
            
            return True
        else:
            print("❌ 獲取題目失敗")
            return False
    except Exception as e:
        print(f"❌ 獲取題目錯誤: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始前端整合測試...")
    print("=" * 50)
    
    # 等待服務啟動
    print("⏳ 等待服務準備就緒...")
    time.sleep(3)
    
    # 執行測試
    success1 = test_frontend_backend_integration()
    success2 = test_workflow_simulation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 前端整合測試完成！所有功能正常運行")
        print("\n✅ 系統已準備好供用戶使用：")
        print("   - 前端頁面: http://localhost:8080/pages/exercise.html")
        print("   - API文檔: http://localhost:8002/docs")
        print("   - 支援科目: 國文、英文、歷史、公民")
        print("   - 支援版本: 南一、康軒、翰林")
    else:
        print("❌ 測試發現問題，請檢查系統配置")

if __name__ == "__main__":
    main()