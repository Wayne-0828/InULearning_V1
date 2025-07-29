#!/bin/bash

# InULearning Docker 啟動腳本
# 作者: AIPE01_group2
# 版本: v1.0.0

set -e

echo "🚀 正在啟動 InULearning 系統..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 Docker Compose 是否安裝
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 建立必要的目錄
echo "📁 建立必要的目錄..."
mkdir -p logs
mkdir -p init-scripts
mkdir -p nginx/conf.d

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "📝 建立 .env 檔案..."
    cp env.docker .env
    echo "✅ .env 檔案已建立，請檢查並修改配置"
fi

# 停止現有容器（如果存在）
echo "🛑 停止現有容器..."
docker compose down --remove-orphans

# 建立並啟動容器
echo "🔨 建立並啟動容器..."
docker compose up --build -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker compose ps

# 檢查健康狀態
echo "🏥 檢查服務健康狀態..."
for service in postgres mongodb redis minio auth-service question-bank-service learning-service nginx student-frontend; do
    echo "檢查 $service..."
    if docker compose exec -T $service curl -f http://localhost:8000/health > /dev/null 2>&1 || \
       docker compose exec -T $service curl -f http://localhost/health > /dev/null 2>&1 || \
       docker compose exec -T $service redis-cli ping > /dev/null 2>&1 || \
       docker compose exec -T $service pg_isready -U inulearning_user -d inulearning > /dev/null 2>&1 || \
       docker compose exec -T $service mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "✅ $service 運行正常"
    else
        echo "⚠️ $service 可能需要更多時間啟動"
    fi
done

echo ""
echo "🎉 InULearning 系統啟動完成！"
echo ""
echo "📋 服務訪問地址："
echo "   🌐 學生端前端: http://localhost:8080"
echo "   🔐 認證服務: http://localhost:8001"
echo "   📚 題庫服務: http://localhost:8002"
echo "   📖 學習服務: http://localhost:8003"
echo "   🗄️ PostgreSQL: localhost:5432"
echo "   📊 MongoDB: localhost:27017"
echo "   🚀 Redis: localhost:6379"
echo "   📦 MinIO: http://localhost:9000 (Console: http://localhost:9001)"
echo ""
echo "🔧 管理命令："
echo "   查看日誌: docker compose logs -f [服務名]"
echo "   停止服務: docker compose down"
echo "   重啟服務: docker compose restart [服務名]"
echo "   查看狀態: docker compose ps"
echo ""
echo "📝 測試帳號："
echo "   學生帳號: student@test.com / password123"
echo "   教師帳號: test_teacher / password123"
echo ""
echo "✨ 開始使用 InULearning 吧！" 