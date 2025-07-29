#!/bin/bash

# InULearning Docker 停止腳本
# 作者: AIPE01_group2
# 版本: v1.0.0

echo "🛑 正在停止 InULearning 系統..."

# 停止所有容器
docker-compose down

echo "✅ InULearning 系統已停止"

# 可選：清理未使用的資源
read -p "是否要清理未使用的 Docker 資源？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理未使用的資源..."
    docker system prune -f
    echo "✅ 清理完成"
fi

echo "👋 再見！" 