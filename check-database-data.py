#!/usr/bin/env python3
"""
檢查資料庫中的已刪除班級和已移除學生資料
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def check_api_endpoint(endpoint, description):
    """檢查 API 端點並顯示結果"""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\n🔍 檢查 {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功")
            print(f"響應資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 分析資料
            if 'data' in data:
                items = data['data']
                if isinstance(items, list):
                    print(f"📊 找到 {len(items)} 個項目")
                    if len(items) > 0:
                        print("📋 第一個項目:")
                        print(json.dumps(items[0], indent=2, ensure_ascii=False))
                else:
                    print(f"📊 資料類型: {type(items)}")
                    print(f"📋 資料內容: {items}")
            else:
                print("📊 響應結構:", list(data.keys()))
                
        elif response.status_code == 401:
            print("❌ 需要認證")
        elif response.status_code == 403:
            print("❌ 權限不足")
        elif response.status_code == 404:
            print("❌ 端點不存在")
        else:
            print(f"❌ 錯誤: {response.text}")
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始檢查資料庫中的已刪除班級和已移除學生資料")
    print("=" * 60)
    
    # 檢查 1: 獲取教師班級關係（包含已刪除）
    check_api_endpoint(
        "/relationships/teacher-class?include_deleted=true",
        "教師班級關係（包含已刪除）"
    )
    
    # 檢查 2: 獲取教師班級關係（不包含已刪除）
    check_api_endpoint(
        "/relationships/teacher-class",
        "教師班級關係（不包含已刪除）"
    )
    
    # 檢查 3: 獲取已移除學生
    check_api_endpoint(
        "/relationships/teacher/removed-students",
        "已移除學生列表"
    )
    
    print("\n" + "=" * 60)
    print("🎯 檢查完成！")
    print("\n分析結果:")
    print("1. 如果狀態碼是 401，需要先登入")
    print("2. 如果狀態碼是 403，需要教師權限")
    print("3. 如果狀態碼是 404，API 端點不存在")
    print("4. 如果狀態碼是 200 但沒有資料，表示資料庫中沒有相關資料")
    print("\n建議:")
    print("1. 確保後端服務正在運行")
    print("2. 確保已經登入教師帳號")
    print("3. 如果沒有資料，可能需要先創建一些測試資料")

if __name__ == "__main__":
    main()
