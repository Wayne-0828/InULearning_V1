#!/usr/bin/env python3
"""
系統整合測試腳本
測試前端到後端的完整流程
"""

import requests
import json
import time

def test_api_endpoints():
    """測試API端點"""
    base_url = "http://localhost:8002"
    
    print("🔍 測試系統整合...")
    
    # 測試基本連接
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 基本連接: {response.status_code}")
    except Exception as e:
        print(f"❌ 基本連接失敗: {e}")
        return False
    
    # 測試API文檔
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ API文檔: {response.status_code}")
    except Exception as e:
        print(f"❌ API文檔失敗: {e}")
    
    # 測試題庫檢查API
    try:
        params = {
            "grade": "7A",
            "edition": "康軒",
            "subject": "國文"
        }
        response = requests.get(f"{base_url}/api/v1/questions/check", params=params, timeout=5)
        print(f"✅ 題庫檢查API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   回應: {data}")
    except Exception as e:
        print(f"❌ 題庫檢查API失敗: {e}")
    
    # 測試獲取題目API
    try:
        params = {
            "grade": "7A",
            "edition": "康軒", 
            "subject": "國文",
            "questionCount": 5
        }
        response = requests.get(f"{base_url}/api/v1/questions/by-conditions", params=params, timeout=5)
        print(f"✅ 獲取題目API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   獲取到 {len(data.get('data', []))} 道題目")
    except Exception as e:
        print(f"❌ 獲取題目API失敗: {e}")
    
    return True

def check_docker_services():
    """檢查Docker服務狀態"""
    import subprocess
    
    print("🐳 檢查Docker服務...")
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'inulearning_mongodb' in result.stdout:
            print("✅ MongoDB服務運行中")
        else:
            print("❌ MongoDB服務未運行")
            
        if 'inulearning_minio' in result.stdout:
            print("✅ MinIO服務運行中")
        else:
            print("❌ MinIO服務未運行")
            
        if 'question_bank_service' in result.stdout:
            print("✅ 題庫服務運行中")
        else:
            print("❌ 題庫服務未運行")
            
    except Exception as e:
        print(f"❌ 檢查Docker服務失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始系統整合測試...")
    
    # 檢查Docker服務
    check_docker_services()
    
    # 等待服務啟動
    print("⏳ 等待服務啟動...")
    time.sleep(5)
    
    # 測試API
    test_api_endpoints()
    
    print("🎉 系統整合測試完成！")

if __name__ == "__main__":
    main()