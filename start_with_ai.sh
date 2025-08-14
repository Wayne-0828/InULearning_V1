#!/bin/bash

# InULearning 完整啟動腳本（包含 AI 服務）
# 使用方法: ./start_with_ai.sh

set -e

echo "🚀 開始啟動 InULearning 系統（包含 AI 服務）"
echo "=================================================="

# 步驟 1: 啟動 Docker 容器
echo "📦 步驟 1: 啟動 Docker 容器..."
docker compose up -d

echo "✅ Docker 容器啟動完成"
echo ""

# 步驟 2: 等待基礎服務啟動
echo "⏳ 步驟 2: 等待基礎服務啟動..."
sleep 30

echo "✅ 基礎服務啟動完成"
echo ""

# 步驟 3: 執行 start.sh 腳本
echo "🔄 步驟 3: 執行系統啟動腳本..."
./start.sh

echo "✅ 系統啟動腳本執行完成"
echo ""

# 步驟 4: 檢查 AI 服務依賴
echo "🔍 步驟 4: 檢查 AI 服務依賴..."

# 檢查 Python 套件
if ! python3 -c "import fastapi, uvicorn, google.generativeai" 2>/dev/null; then
    echo "⚠️  安裝 AI 服務依賴套件..."
    pip install fastapi uvicorn pydantic google-generativeai python-dotenv
fi

echo "✅ AI 服務依賴檢查完成"
echo ""

# 步驟 5: 啟動 AI 服務
echo "🤖 步驟 5: 啟動 AI 服務..."
echo "📍 AI 服務將在 http://localhost:8004 運行"
echo "📊 API 文檔: http://localhost:8004/docs"
echo "🧪 測試端點: http://localhost:8004/test"
echo ""

# 在背景啟動 AI 服務
python3 start_ai_service.py &
AI_SERVICE_PID=$!

# 等待 AI 服務啟動
sleep 10

# 檢查 AI 服務是否正常運行
if curl -s http://localhost:8004/health > /dev/null; then
    echo "✅ AI 服務啟動成功"
else
    echo "⚠️  AI 服務啟動中，請稍後檢查..."
fi

echo ""
echo "🎉 InULearning 系統啟動完成！"
echo "=================================================="
echo "🎯 📋 服務訪問地址："
echo "  🏠 統一入口: http://localhost/"
echo "  🎓 學生端: http://localhost:8080"
echo "  👨‍💼 管理員端: http://localhost:8081"
echo "  👪 家長端: http://localhost:8082"
echo "  👨‍🏫 教師端: http://localhost:8083"
echo ""
echo "🤖 AI 服務地址："
echo "  📊 API 文檔: http://localhost:8004/docs"
echo "  🧪 測試端點: http://localhost:8004/test"
echo "  📋 健康檢查: http://localhost:8004/health"
echo ""
echo "📝 測試帳號（密碼都是 password123）："
echo "  👨‍🎓 學生: student01@test.com"
echo "  👨‍🏫 教師: teacher01@test.com"
echo "  👪 家長: parent01@test.com"
echo "  👨‍💼 管理員: admin01@test.com"
echo ""
echo "🔧 管理命令："
echo "  查看所有服務: docker compose ps"
echo "  停止所有服務: docker compose down"
echo "  停止 AI 服務: kill $AI_SERVICE_PID"
echo ""
echo "✨ 開始使用 InULearning 吧！"
echo "=================================================="

# 保存 AI 服務 PID 到檔案
echo $AI_SERVICE_PID > .ai_service.pid

echo "💡 提示："
echo "  • AI 服務 PID 已保存到 .ai_service.pid"
echo "  • 如需停止 AI 服務，請執行: kill \$(cat .ai_service.pid)"
echo "  • 如需重新啟動 AI 服務，請執行: python3 start_ai_service.py"
