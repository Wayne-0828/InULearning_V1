#!/usr/bin/env python3
"""
測試題目篩選功能
驗證API是否根據不同條件正確返回不同題目
"""

import requests
import json
import time

def test_question_filtering():
    """測試題目篩選功能"""
    print("🔍 測試題目篩選功能...")
    
    api_base = "http://localhost:8002/api/v1"
    
    # 測試不同的條件組合
    test_cases = [
        {
            "name": "康軒國文",
            "params": {"grade": "7A", "edition": "康軒", "subject": "國文", "questionCount": 3}
        },
        {
            "name": "翰林英文", 
            "params": {"grade": "7A", "edition": "翰林", "subject": "英文", "questionCount": 3}
        },
        {
            "name": "南一公民",
            "params": {"grade": "7A", "edition": "南一", "subject": "公民", "questionCount": 3}
        },
        {
            "name": "康軒歷史",
            "params": {"grade": "7A", "edition": "康軒", "subject": "歷史", "questionCount": 3}
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        name = test_case["name"]
        params = test_case["params"]
        
        print(f"\n📝 測試 {name}...")
        
        try:
            # 1. 檢查題庫
            check_params = {k: v for k, v in params.items() if k != 'questionCount'}
            response = requests.get(f"{api_base}/questions/check", params=check_params, timeout=5)
            
            if response.status_code == 200:
                check_data = response.json()
                count = check_data['data']['count']
                print(f"  ✅ 題庫檢查: {count}題可用")
            else:
                print(f"  ❌ 題庫檢查失敗: {response.status_code}")
                continue
            
            # 2. 獲取題目
            response = requests.get(f"{api_base}/questions/by-conditions", params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['success'] and data['data']:
                    questions = data['data']
                    print(f"  ✅ 獲取題目: {len(questions)}題")
                    
                    # 驗證題目內容
                    first_question = questions[0]
                    actual_subject = first_question.get('subject', 'N/A')
                    actual_publisher = first_question.get('publisher', 'N/A')
                    actual_grade = first_question.get('grade', 'N/A')
                    
                    print(f"  📋 第一題資訊:")
                    print(f"    題目: {first_question.get('question', 'N/A')[:50]}...")
                    print(f"    科目: {actual_subject}")
                    print(f"    出版社: {actual_publisher}")
                    print(f"    年級: {actual_grade}")
                    print(f"    章節: {first_question.get('chapter', 'N/A')}")
                    
                    # 驗證篩選是否正確
                    expected_subject = params['subject']
                    expected_publisher = params['edition']
                    expected_grade = params['grade']
                    
                    if (actual_subject == expected_subject and 
                        actual_publisher == expected_publisher and
                        actual_grade == expected_grade):
                        print(f"  ✅ 篩選正確")
                        results[name] = "✅ 正確"
                    else:
                        print(f"  ❌ 篩選錯誤!")
                        print(f"    期望: {expected_grade} {expected_publisher} {expected_subject}")
                        print(f"    實際: {actual_grade} {actual_publisher} {actual_subject}")
                        results[name] = "❌ 錯誤"
                else:
                    print(f"  ❌ API返回無效資料")
                    results[name] = "❌ 無資料"
            else:
                print(f"  ❌ 獲取題目失敗: {response.status_code}")
                results[name] = f"❌ HTTP {response.status_code}"
                
        except Exception as e:
            print(f"  ❌ 測試失敗: {e}")
            results[name] = f"❌ 異常: {e}"
    
    # 總結結果
    print("\n" + "="*50)
    print("📊 篩選測試結果總結:")
    print("="*50)
    
    for name, result in results.items():
        print(f"{name:15} : {result}")
    
    # 檢查是否所有測試都通過
    all_passed = all("✅" in result for result in results.values())
    
    if all_passed:
        print("\n🎉 所有篩選測試通過！題目篩選功能正常工作")
        return True
    else:
        print("\n❌ 部分篩選測試失敗，需要進一步檢查")
        return False

def test_chapter_filtering():
    """測試章節篩選功能"""
    print("\n🔍 測試章節篩選功能...")
    
    api_base = "http://localhost:8002/api/v1"
    
    # 測試有章節和無章節的情況
    test_cases = [
        {
            "name": "康軒國文(無章節)",
            "params": {"grade": "7A", "edition": "康軒", "subject": "國文", "questionCount": 2}
        },
        {
            "name": "康軒國文(指定章節)",
            "params": {"grade": "7A", "edition": "康軒", "subject": "國文", "chapter": "夏夜", "questionCount": 2}
        }
    ]
    
    for test_case in test_cases:
        name = test_case["name"]
        params = test_case["params"]
        
        print(f"\n📝 測試 {name}...")
        
        try:
            response = requests.get(f"{api_base}/questions/by-conditions", params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data['success'] and data['data']:
                    questions = data['data']
                    print(f"  ✅ 獲取題目: {len(questions)}題")
                    
                    # 顯示章節資訊
                    chapters = set(q.get('chapter', 'N/A') for q in questions)
                    print(f"  📚 涉及章節: {', '.join(chapters)}")
                    
                    if 'chapter' in params:
                        # 檢查是否所有題目都來自指定章節
                        expected_chapter = params['chapter']
                        all_correct = all(q.get('chapter') == expected_chapter for q in questions)
                        if all_correct:
                            print(f"  ✅ 章節篩選正確")
                        else:
                            print(f"  ❌ 章節篩選失敗")
                else:
                    print(f"  ❌ 無法獲取題目")
            else:
                print(f"  ❌ API調用失敗: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 測試失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始題目篩選測試...")
    print("=" * 50)
    
    # 等待服務準備就緒
    print("⏳ 等待服務準備就緒...")
    time.sleep(3)
    
    # 執行測試
    success1 = test_question_filtering()
    test_chapter_filtering()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 題目篩選功能測試完成！")
        print("✅ 系統能夠正確根據用戶選擇的條件篩選題目")
    else:
        print("❌ 題目篩選功能存在問題，需要修復")

if __name__ == "__main__":
    main()