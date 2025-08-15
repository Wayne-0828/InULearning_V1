#!/usr/bin/env python3
"""
API 連接測試腳本
測試 InULearning 系統的各個 API 端點是否正常運作
"""

import json
from datetime import datetime

import requests

# API 基礎 URL
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api/v1"

# 測試端點列表
ENDPOINTS = [
    # 健康檢查端點
    {"name": "認證服務健康檢查", "url": f"{API_BASE}/auth/health", "method": "GET"},
    {"name": "學習服務健康檢查", "url": f"{API_BASE}/learning/health", "method": "GET"},
    {
        "name": "題庫服務健康檢查",
        "url": f"{API_BASE}/questions/health",
        "method": "GET",
    },
    # 直接服務端點
    {"name": "認證服務直接", "url": "http://localhost:8001/health", "method": "GET"},
    {"name": "題庫服務直接", "url": "http://localhost:8002/health", "method": "GET"},
    {"name": "學習服務直接", "url": "http://localhost:8003/health", "method": "GET"},
    # 功能端點
    {
        "name": "題庫檢查",
        "url": f"{API_BASE}/questions/check",
        "method": "GET",
        "params": {"grade": "7A", "edition": "翰林", "subject": "英文"},
    },
    {
        "name": "學習統計",
        "url": f"{API_BASE}/learning/sessions/statistics/summary",
        "method": "GET",
    },
]


def test_endpoint(endpoint):
    """測試單個端點"""
    try:
        print(f"🔍 測試: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")

        if endpoint["method"] == "GET":
            response = requests.get(
                endpoint["url"], params=endpoint.get("params", {}), timeout=10
            )
        else:
            response = requests.request(
                endpoint["method"],
                endpoint["url"],
                json=endpoint.get("data", {}),
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
                else:
                    print(
                        f"   📄 回應類型: {type(data)}, 長度: {len(data) if hasattr(data, '__len__') else 'N/A'}"
                    )
            except:
                print(f"   📄 回應: {response.text[:200]}...")
        else:
            print(f"   ❌ 失敗 (狀態碼: {response.status_code})")
            print(f"   📄 錯誤: {response.text[:200]}")

        print()
        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print(f"   ❌ 連接失敗: 無法連接到服務")
        print()
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 超時: 請求超過 10 秒")
        print()
        return False
    except Exception as e:
        print(f"   ❌ 錯誤: {str(e)}")
        print()
        return False


def main():
    """主測試函數"""
    print("=" * 60)
    print("🚀 InULearning API 連接測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    success_count = 0
    total_count = len(ENDPOINTS)

    for endpoint in ENDPOINTS:
        if test_endpoint(endpoint):
            success_count += 1

    print("=" * 60)
    print("📊 測試結果摘要")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    print(f"📈 成功率: {(success_count/total_count)*100:.1f}%")
    print("=" * 60)

    if success_count == 0:
        print("⚠️  建議檢查:")
        print("   1. Docker 容器是否正在運行: docker compose ps")
        print("   2. 服務是否已啟動: docker compose logs [service-name]")
        print("   3. 端口是否被佔用: netstat -tulpn | grep :8080")
        print("   4. 防火牆設定是否正確")
    elif success_count < total_count:
        print("⚠️  部分服務可能未正常運行，請檢查相關服務狀態")
    else:
        print("🎉 所有 API 端點都正常運作！")


if __name__ == "__main__":
    main()
