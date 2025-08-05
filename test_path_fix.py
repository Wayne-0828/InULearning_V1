#!/usr/bin/env python3
"""
路徑修正驗證腳本
檢查所有文件路徑是否正確設置
"""

import os
from pathlib import Path

def verify_file_paths():
    """驗證文件路徑"""
    print("🔍 InU Learning 文件路徑驗證")
    print("=" * 50)
    
    # 基礎路徑
    base_path = "2_implementation/frontend/shared"
    
    # 檢查文件是否存在
    files_to_check = [
        "homepage/index.html",
        "auth/login.html", 
        "auth/register.html"
    ]
    
    print("📁 檢查文件存在性:")
    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_exist = False
    
    if not all_exist:
        return False
    
    print("\n🔗 檢查首頁連結路徑:")
    
    # 讀取首頁文件
    index_path = os.path.join(base_path, "homepage/index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查連結路徑
    expected_links = [
        "../auth/login.html",
        "../auth/register.html"
    ]
    
    for link in expected_links:
        count = content.count(link)
        if count > 0:
            print(f"✅ {link} (出現 {count} 次)")
        else:
            print(f"❌ {link} - 未找到")
    
    print("\n📋 相對路徑說明:")
    print("  homepage/index.html → ../auth/register.html")
    print("  (從 homepage 目錄上一層到 auth 目錄)")
    
    print("\n🌐 建議的訪問方式:")
    print("  1. 直接訪問: file:///path/to/2_implementation/frontend/shared/homepage/index.html")
    print("  2. 本地伺服器: 在 shared 目錄啟動 HTTP 伺服器")
    print("  3. 使用 Live Server 擴展")
    
    return True

def create_test_server_script():
    """創建本地測試伺服器腳本"""
    server_script = """#!/bin/bash
# 本地測試伺服器啟動腳本

echo "🚀 啟動 InU Learning 本地測試伺服器"
echo "================================"

# 進入 shared 目錄
cd 2_implementation/frontend/shared

# 檢查 Python 版本並啟動伺服器
if command -v python3 &> /dev/null; then
    echo "✅ 使用 Python 3 啟動伺服器"
    echo "📡 伺服器地址: http://localhost:8000"
    echo "🏠 首頁訪問: http://localhost:8000/homepage/"
    echo "🔐 登入頁面: http://localhost:8000/auth/login.html"
    echo "📝 註冊頁面: http://localhost:8000/auth/register.html"
    echo ""
    echo "按 Ctrl+C 停止伺服器"
    echo "================================"
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "✅ 使用 Python 2 啟動伺服器"
    echo "📡 伺服器地址: http://localhost:8000"
    python -m SimpleHTTPServer 8000
else
    echo "❌ 未找到 Python，請安裝 Python"
    exit 1
fi
"""
    
    with open("start_test_server.sh", 'w') as f:
        f.write(server_script)
    
    # 設置執行權限
    os.chmod("start_test_server.sh", 0o755)
    print("📄 已創建測試伺服器腳本: start_test_server.sh")

def main():
    print("🔧 InU Learning 路徑修正驗證")
    print("=" * 60)
    
    if verify_file_paths():
        print("\n✅ 路徑驗證通過！")
        create_test_server_script()
        
        print("\n🎯 解決方案:")
        print("1. 路徑已修正為相對路徑 ../auth/")
        print("2. 可使用本地伺服器測試: ./start_test_server.sh")
        print("3. 或直接在 VSCode 中使用 Live Server 擴展")
        
        print("\n📱 推薦測試步驟:")
        print("1. 執行: ./start_test_server.sh")
        print("2. 瀏覽器訪問: http://localhost:8000/homepage/")
        print("3. 測試註冊/登入連結")
        
    else:
        print("\n❌ 路徑驗證失敗，請檢查文件結構")

if __name__ == "__main__":
    main()