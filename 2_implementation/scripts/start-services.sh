#!/bin/bash

# InULearning 服務啟動腳本
# 適用於 WSL 環境

echo "🚀 正在啟動 InULearning 服務..."

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker"
    exit 1
fi

# 檢查 docker-compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安裝"
    exit 1
fi

# 進入專案根目錄
cd "$(dirname "$0")/../.."

echo "📁 當前目錄: $(pwd)"

# 停止現有服務
echo "🛑 停止現有服務..."
docker-compose down

# 清理舊的容器和映像（可選）
read -p "是否清理舊的容器和映像？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理舊的容器和映像..."
    docker system prune -f
fi

# 構建並啟動服務
echo "🔨 構建並啟動服務..."
docker-compose up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查服務狀態
echo "📊 檢查服務狀態..."
docker-compose ps

# 檢查各服務健康狀態
echo "🏥 檢查服務健康狀態..."

services=(
    "http://localhost:8001/health:認證服務"
    "http://localhost:8002/health:題庫服務"
    "http://localhost:8003/health:學習服務"
    "http://localhost:8004/health:AI分析服務"
    "http://localhost:80:Nginx網關"
    "http://localhost:8080:學生端"
    "http://localhost:8081:管理端"
    "http://localhost:8082:家長端"
    "http://localhost:8083:教師端"
)

for service in "${services[@]}"; do
    url="${service%:*}"
    name="${service#*:}"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ $name: 正常運行"
    else
        echo "❌ $name: 無法連接"
    fi
done

echo ""
echo "🎉 服務啟動完成！"
echo ""
echo "📱 前端應用訪問地址："
echo "   學生端: http://localhost:8080"
echo "   管理端: http://localhost:8081"
echo "   家長端: http://localhost:8082"
echo "   教師端: http://localhost:8083"
echo ""
echo "🔧 API服務地址："
echo "   認證服務: http://localhost:8001"
echo "   題庫服務: http://localhost:8002"
echo "   學習服務: http://localhost:8003"
echo "   AI分析服務: http://localhost:8004"
echo ""
echo "💾 資料庫連接："
echo "   PostgreSQL: localhost:5432"
echo "   MongoDB: localhost:27017"
echo "   Redis: localhost:6379"
echo "   MinIO: http://localhost:9001"
echo ""
echo "📋 查看日誌: docker-compose logs -f [服務名稱]"
echo "🛑 停止服務: docker-compose down"
echo ""