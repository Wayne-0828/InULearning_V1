#!/usr/bin/env python3
"""
學習服務 API 測試腳本
"""

import json
from datetime import datetime

import requests

BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api/v1"


def login_teacher():
    """登入教師帳號"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "teacher01@test.com", "password": "password123"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"登入失敗: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"登入錯誤: {str(e)}")
        return None


def test_learning_endpoints(token):
    """測試學習服務端點"""
    headers = {"Authorization": f"Bearer {token}"}

    # 測試端點列表
    endpoints = [
        f"{API_BASE}/learning/teacher/students",
        f"{API_BASE}/learning/statistics/summary",
        f"{API_BASE}/learning/records",
        f"{API_BASE}/learning/recent",
        f"{API_BASE}/learning/",  # 獲取會話列表
    ]

    print("🔍 測試學習服務端點:")
    print("=" * 50)

    for url in endpoints:
        try:
            print(f"測試: {url}")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"✅ 成功 (200)")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📄 回應: 列表，包含 {len(data)} 項目")
                    elif isinstance(data, dict):
                        print(
                            f"   📄 回應: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}..."
                        )
                except:
                    print(f"   📄 回應: {response.text[:100]}...")
            else:
                print(f"❌ 失敗 ({response.status_code})")
                print(f"   📄 錯誤: {response.text[:100]}")

            print()

        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
            print()


def main():
    print("🚀 學習服務 API 測試")
    print("=" * 50)

    # 登入
    token = login_teacher()
    if not token:
        print("❌ 無法獲取認證 token，測試終止")
        return

    print("✅ 教師登入成功")
    print()

    # 測試端點
    test_learning_endpoints(token)


if __name__ == "__main__":
    main()
