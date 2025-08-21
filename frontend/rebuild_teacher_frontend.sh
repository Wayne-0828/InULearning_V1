#!/bin/bash

echo "🔄 重新構建教師端前端容器..."
echo "=================================="

# 停止教師端容器
echo "1. 停止教師端容器..."
docker compose stop teacher-frontend

# 重新構建教師端容器
echo "2. 重新構建教師端容器..."
docker compose build --no-cache teacher-frontend

# 啟動教師端容器
echo "3. 啟動教師端容器..."
docker compose up -d teacher-frontend

# 檢查容器狀態
echo "4. 檢查容器狀態..."
docker compose ps teacher-frontend

echo ""
echo "✅ 重新構建完成！"
echo "🌐 請訪問: http://localhost:8083/pages/students-enhanced.html"
echo "💡 如果仍然看不到更新，請清除瀏覽器快取 (Ctrl+F5)"