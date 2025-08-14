#!/bin/bash

# InULearning 快速重啟腳本
# 用於系統已配置完成後的快速重啟

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🔄 InULearning 快速重啟"
echo "======================="

# 檢查 Docker 是否運行
if ! docker info &> /dev/null; then
    log_error "Docker 服務未運行，請先啟動 Docker"
    exit 1
fi

# 停止所有服務
log_info "停止現有服務..."
docker compose down

# 快速啟動
log_info "重新啟動服務..."
docker compose up -d

# 等待服務就緒
log_info "等待服務啟動..."
sleep 20

# 檢查狀態
log_info "檢查服務狀態..."
docker compose ps

log_success "快速重啟完成！"

echo ""
echo "📋 服務訪問地址："
echo "   🎓 學生端: http://localhost:8080"
echo "   👨‍💼 管理員端: http://localhost:8081" 
echo "   👪 家長端: http://localhost:8082"
echo "   👨‍🏫 教師端: http://localhost:8083"
echo ""
echo "如需完整重新部署，請使用: ./start.sh" 