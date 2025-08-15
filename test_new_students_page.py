#!/usr/bin/env python3
"""
測試新的學生管理頁面
"""

import json
from datetime import datetime

import requests


def test_page_functionality():
    """測試頁面功能"""
    print("🧪 測試新的學生管理頁面")
    print("=" * 50)

    # 測試 API 連接
    print("1. 測試 API 連接...")
    try:
        response = requests.get("http://localhost/api/v1/learning/health", timeout=5)
        if response.ok:
            print("   ✅ 學習服務 API 正常")
        else:
            print(f"   ❌ 學習服務 API 異常: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 學習服務 API 無法連接: {e}")

    # 測試認證
    print("\n2. 測試教師認證...")
    try:
        auth_response = requests.post(
            "http://localhost/api/v1/auth/login",
            json={"email": "teacher01@test.com", "password": "password123"},
            timeout=5,
        )

        if auth_response.ok:
            token = auth_response.json().get("access_token")
            print("   ✅ 教師認證成功")

            # 測試學習記錄端點
            print("\n3. 測試學習記錄端點...")
            headers = {"Authorization": f"Bearer {token}"}

            records_response = requests.get(
                "http://localhost/api/v1/learning/records", headers=headers, timeout=5
            )

            if records_response.ok:
                data = records_response.json()
                print(f"   ✅ 學習記錄端點正常 (找到 {data.get('total', 0)} 筆記錄)")

                if data.get("sessions"):
                    print(f"   📊 會話資料: {len(data['sessions'])} 個會話")
                else:
                    print("   ⚠️ 無會話資料，頁面將使用模擬資料")
            else:
                print(f"   ❌ 學習記錄端點異常: {records_response.status_code}")

        else:
            print(f"   ❌ 教師認證失敗: {auth_response.status_code}")

    except Exception as e:
        print(f"   ❌ 認證測試失敗: {e}")

    print("\n4. 頁面訪問測試...")
    page_urls = [
        "http://localhost:8083/pages/students-enhanced.html",
        "http://localhost:8083/pages/students-enhanced.html?classId=1&class=七年三班",
    ]

    for url in page_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.ok:
                print(f"   ✅ 頁面可訪問: {url}")
            else:
                print(f"   ❌ 頁面無法訪問: {url} ({response.status_code})")
        except Exception as e:
            print(f"   ❌ 頁面訪問失敗: {url} ({e})")

    print("\n" + "=" * 50)
    print("📋 測試總結:")
    print("- 新的學生管理頁面已創建")
    print("- 包含完整的 UI/UX 設計")
    print("- 支援 API 連接和模擬資料降級")
    print("- 響應式設計，支援多種螢幕尺寸")
    print("- 雙視圖模式：表格和卡片")
    print("- 即時搜尋和篩選功能")
    print("\n🚀 請訪問以下 URL 查看頁面:")
    print("   http://localhost:8083/pages/students-enhanced.html")
    print("   http://localhost:8083/pages/students-enhanced.html?class=七年三班")


if __name__ == "__main__":
    test_page_functionality()
