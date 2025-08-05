#!/bin/bash
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
