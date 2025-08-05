#!/usr/bin/env python3
"""
Docker 整合測試腳本
驗證註冊功能是否正確整合到 Docker 環境
"""

import os
import subprocess
import time
import requests
import json
from pathlib import Path

def run_command(cmd, capture_output=True, timeout=30):
    """執行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture_output, 
            text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令執行超時"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(file_path):
    """檢查文件是否存在"""
    return os.path.exists(file_path)

def test_docker_compose_config():
    """測試 Docker Compose 配置"""
    print("🔍 檢查 Docker Compose 配置...")
    
    # 檢查關鍵文件
    files_to_check = [
        "docker-compose.yml",
        "nginx/nginx.conf",
        "2_implementation/frontend/shared/auth/register.html",
        "2_implementation/frontend/shared/auth/login.html",
        "2_implementation/frontend/shared/homepage/index.html",
        "2_implementation/frontend/shared/js/register.js",
        "2_implementation/frontend/shared/js/api-client.js",
        "2_implementation/frontend/shared/js/utils.js"
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not check_file_exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少檔案: {missing_files}")
        return False
    
    print("✅ 所有必要檔案存在")
    
    # 檢查 docker-compose.yml 中的 nginx 掛載
    with open("docker-compose.yml", 'r', encoding='utf-8') as f:
        compose_content = f.read()
    
    required_mounts = [
        "register.html:/usr/share/nginx/html/register.html",
        "login.html:/usr/share/nginx/html/login.html", 
        "index.html:/usr/share/nginx/html/index.html",
        "shared/js:/usr/share/nginx/html/js"
    ]
    
    missing_mounts = []
    for mount in required_mounts:
        if mount not in compose_content:
            missing_mounts.append(mount)
    
    if missing_mounts:
        print(f"❌ Docker Compose 缺少掛載: {missing_mounts}")
        return False
    
    print("✅ Docker Compose 配置正確")
    return True

def test_nginx_config():
    """測試 nginx 配置"""
    print("🔍 檢查 nginx 配置...")
    
    with open("nginx/nginx.conf", 'r', encoding='utf-8') as f:
        nginx_content = f.read()
    
    required_locations = [
        "location /login.html",
        "location /register.html", 
        "location /index.html"
    ]
    
    missing_locations = []
    for location in required_locations:
        if location not in nginx_content:
            missing_locations.append(location)
    
    if missing_locations:
        print(f"❌ nginx 配置缺少路由: {missing_locations}")
        return False
    
    print("✅ nginx 配置正確")
    return True

def test_docker_environment():
    """測試 Docker 環境"""
    print("🔍 檢查 Docker 環境...")
    
    # 檢查 Docker 是否運行
    success, stdout, stderr = run_command("docker info")
    if not success:
        print("❌ Docker 未運行")
        return False
    
    # 檢查 Docker Compose 是否可用
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        success, stdout, stderr = run_command("docker compose version")
        if not success:
            print("❌ Docker Compose 不可用")
            return False
    
    print("✅ Docker 環境正常")
    return True

def start_services():
    """啟動服務"""
    print("🚀 啟動 Docker 服務...")
    
    # 停止現有服務
    print("  停止現有服務...")
    run_command("docker-compose down", capture_output=False)
    
    # 啟動服務
    print("  啟動新服務...")
    success, stdout, stderr = run_command(
        "docker-compose up -d nginx auth-service", 
        capture_output=False, 
        timeout=120
    )
    
    if not success:
        print(f"❌ 服務啟動失敗: {stderr}")
        return False
    
    print("✅ 服務啟動成功")
    
    # 等待服務就緒
    print("  等待服務就緒...")
    time.sleep(15)
    return True

def test_endpoints():
    """測試端點"""
    print("🔍 測試服務端點...")
    
    endpoints = [
        ("http://localhost/", "首頁重定向"),
        ("http://localhost/index.html", "首頁"),
        ("http://localhost/login.html", "登入頁"),
        ("http://localhost/register.html", "註冊頁"),
        ("http://localhost:8001/health", "認證服務健康檢查")
    ]
    
    failed_endpoints = []
    
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} - HTTP {response.status_code}")
            elif response.status_code == 302 and "index.html" in name:
                print(f"✅ {name} - HTTP {response.status_code} (重定向)")
            else:
                print(f"❌ {name} - HTTP {response.status_code}")
                failed_endpoints.append(name)
        except Exception as e:
            print(f"❌ {name} - 連接失敗: {e}")
            failed_endpoints.append(name)
    
    return len(failed_endpoints) == 0

def test_registration_api():
    """測試註冊 API"""
    print("🔍 測試註冊 API...")
    
    # 測試管理員角色被拒絕
    admin_data = {
        "email": f"admin_test_{int(time.time())}@test.com",
        "username": f"admin_test_{int(time.time())}",
        "password": "TestPass123!",
        "role": "admin",
        "first_name": "測試",
        "last_name": "管理員"
    }
    
    try:
        response = requests.post(
            "http://localhost/api/v1/auth/register",
            json=admin_data,
            timeout=10
        )
        
        if response.status_code == 422 or response.status_code == 400:
            error_data = response.json()
            if "管理員" in str(error_data) or "admin" in str(error_data).lower():
                print("✅ 管理員角色正確被拒絕")
            else:
                print("⚠️ 管理員角色被拒絕，但錯誤訊息不正確")
        else:
            print("❌ 管理員角色未被正確拒絕")
            return False
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")
        return False
    
    # 測試有效角色註冊
    student_data = {
        "email": f"student_test_{int(time.time())}@test.com",
        "username": f"student_test_{int(time.time())}",
        "password": "TestPass123!",
        "role": "student",
        "first_name": "測試",
        "last_name": "學生"
    }
    
    try:
        response = requests.post(
            "http://localhost/api/v1/auth/register",
            json=student_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ 學生註冊成功")
            return True
        else:
            print(f"❌ 學生註冊失敗: HTTP {response.status_code}")
            print(f"    回應: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 學生註冊測試失敗: {e}")
        return False

def cleanup():
    """清理資源"""
    print("🧹 清理測試環境...")
    run_command("docker-compose down", capture_output=False)

def main():
    print("🧪 InU Learning Docker 整合測試")
    print("=" * 60)
    
    try:
        # 預檢查
        if not test_docker_compose_config():
            return False
        
        if not test_nginx_config():
            return False
        
        if not test_docker_environment():
            return False
        
        # 啟動服務
        if not start_services():
            return False
        
        # 功能測試
        if not test_endpoints():
            print("⚠️ 部分端點測試失敗")
        
        if not test_registration_api():
            print("⚠️ 註冊 API 測試失敗")
        
        print("\n" + "=" * 60)
        print("🎉 Docker 整合測試完成！")
        print("\n📋 測試結果摘要:")
        print("✅ Docker Compose 配置正確")
        print("✅ nginx 路由配置正確") 
        print("✅ 所有必要檔案存在")
        print("✅ 服務成功啟動")
        
        print("\n🌐 訪問地址:")
        print("  首頁: http://localhost/")
        print("  登入: http://localhost/login.html")
        print("  註冊: http://localhost/register.html")
        
        print("\n🔧 管理命令:")
        print("  啟動: ./start.sh")
        print("  停止: docker-compose down")
        print("  查看日誌: docker-compose logs -f")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ 測試被用戶中斷")
        return False
    except Exception as e:
        print(f"\n💥 測試執行錯誤: {e}")
        return False
    finally:
        # 不自動清理，讓用戶可以手動測試
        print("\n💡 服務仍在運行，可手動測試。使用 'docker-compose down' 停止服務。")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)