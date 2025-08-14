#!/bin/bash

# InULearning Learning Service 測試執行腳本
# 用於在虛擬環境中執行各種測試

set -e  # 遇到錯誤立即退出

echo "🚀 InULearning Learning Service 測試執行"
echo "=========================================="

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境不存在，請先運行 setup_test_env.sh"
    exit 1
fi

# 激活虛擬環境
echo "🔌 激活虛擬環境..."
source venv/bin/activate

# 檢查服務是否運行
echo "🔍 檢查服務狀態..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ 服務正在運行"
else
    echo "⚠️  服務未運行，正在啟動..."
    python run.py &
    SERVICE_PID=$!
    
    # 等待服務啟動
    echo "⏳ 等待服務啟動..."
    for i in {1..30}; do
        if curl -s http://localhost:8002/health > /dev/null 2>&1; then
            echo "✅ 服務啟動成功"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo "❌ 服務啟動超時"
        kill $SERVICE_PID 2>/dev/null || true
        exit 1
    fi
fi

echo ""
echo "📋 開始執行測試..."
echo ""

# 1. 運行環境測試
echo "1️⃣  運行環境測試..."
python test_setup.py
echo ""

# 2. 運行單元測試
echo "2️⃣  運行單元測試..."
pytest tests/ -v --tb=short
echo ""

# 3. 運行 API 測試
echo "3️⃣  運行 API 測試..."
python test_environment/test_api.py
echo ""

# 4. 運行覆蓋率測試
echo "4️⃣  運行覆蓋率測試..."
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
echo ""

# 5. 生成測試報告
echo "5️⃣  生成測試報告..."
echo "📊 測試報告已生成:"
echo "   - HTML 覆蓋率報告: htmlcov/index.html"
echo "   - 終端覆蓋率報告: 見上方輸出"

# 清理
if [ ! -z "$SERVICE_PID" ]; then
    echo ""
    echo "🧹 清理測試環境..."
    kill $SERVICE_PID 2>/dev/null || true
fi

echo ""
echo "🎉 測試執行完成！"
echo ""
echo "📋 測試結果摘要:"
echo "   - 環境測試: 檢查開發環境配置"
echo "   - 單元測試: 測試核心功能邏輯"
echo "   - API 測試: 測試 HTTP 端點"
echo "   - 覆蓋率測試: 檢查代碼覆蓋率"
echo ""
echo "📚 查看詳細結果:"
echo "   - API 文檔: http://localhost:8002/docs"
echo "   - 健康檢查: http://localhost:8002/health" 