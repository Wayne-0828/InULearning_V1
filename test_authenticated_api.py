#!/usr/bin/env python3
"""
認證 API 測試腳本
測試需要認證的 API 端點
"""

import json
from datetime import datetime

import requests

# API 基礎 URL
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api/v1"

# 測試用戶憑證
TEST_CREDENTIALS = {
    "student": {"email": "student01@test.com", "password": "password123"},
    "teacher": {"email": "teacher01@test.com", "password": "password123"},
    "parent": {"email": "parent01@test.com", "password": "password123"},
    "admin": {"email": "admin01@test.com", "password": "password123"},
}


def login_user(role):
    """登入用戶並獲取 token"""
    try:
        print(f"🔐 嘗試登入 {role}...")

        response = requests.post(
            f"{API_BASE}/auth/login", json=TEST_CREDENTIALS[role], timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print(f"   ✅ {role} 登入成功")
                return token
            else:
                print(f"   ❌ {role} 登入失敗: 沒有收到 token")
                return None
        else:
            print(f"   ❌ {role} 登入失敗: {response.status_code}")
            print(f"   📄 錯誤: {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ {role} 登入錯誤: {str(e)}")
        return None


def test_authenticated_endpoint(endpoint, token):
    """測試需要認證的端點"""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        print(f"🔍 測試: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")

        response = requests.get(
            endpoint["url"],
            headers=headers,
            params=endpoint.get("params", {}),
            timeout=10,
        )

        if response.status_code == 200:
            print(f"   ✅ 成功 (狀態碼: {response.status_code})")
            try:
                data = response.json()
                if isinstance(data, dict) and len(data) <= 5:
                    print(
                        f"   📄 回應: {json.dumps(data, ensure_ascii=False, indent=2)}"
                    )
                elif isinstance(data, list):
                    print(f"   📄 回應: 列表，包含 {len(data)} 項目")
                    if len(data) > 0:
                        print(
                            f"   📄 第一項: {json.dumps(data[0], ensure_ascii=False, indent=2)}"
                        )
                else:
                    print(f"   📄 回應類型: {type(data)}")
            except:
                print(f"   📄 回應: {response.text[:200]}...")
        else:
            print(f"   ❌ 失敗 (狀態碼: {response.status_code})")
            print(f"   📄 錯誤: {response.text[:200]}")

        print()
        return response.status_code == 200

    except Exception as e:
        print(f"   ❌ 錯誤: {str(e)}")
        print()
        return False


def main():
    """主測試函數"""
    print("=" * 60)
    print("🔐 InULearning 認證 API 測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # 測試教師相關端點
    teacher_token = login_user("teacher")

    if teacher_token:
        print("\n📚 測試教師相關端點:")
        teacher_endpoints = [
            {
                "name": "教師學生記錄",
                "url": f"{API_BASE}/learning/records/teacher/students",
            },
            {
                "name": "學習統計摘要",
                "url": f"{API_BASE}/learning/sessions/statistics/summary",
            },
            {"name": "學習記錄", "url": f"{API_BASE}/learning/history/records"},
            {"name": "學習統計", "url": f"{API_BASE}/learning/history/statistics"},
        ]

        success_count = 0
        for endpoint in teacher_endpoints:
            if test_authenticated_endpoint(endpoint, teacher_token):
                success_count += 1

        print(f"📊 教師端點測試結果: {success_count}/{len(teacher_endpoints)} 成功")

    # 測試學生相關端點
    student_token = login_user("student")

    if student_token:
        print("\n🎓 測試學生相關端點:")
        student_endpoints = [
            {"name": "學生記錄", "url": f"{API_BASE}/learning/records/student/records"},
            {
                "name": "學生統計",
                "url": f"{API_BASE}/learning/records/student/statistics",
            },
            {"name": "最近學習", "url": f"{API_BASE}/learning/history/recent"},
        ]

        success_count = 0
        for endpoint in student_endpoints:
            if test_authenticated_endpoint(endpoint, student_token):
                success_count += 1

        print(f"📊 學生端點測試結果: {success_count}/{len(student_endpoints)} 成功")

    print("=" * 60)
    print("✅ 認證 API 測試完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
