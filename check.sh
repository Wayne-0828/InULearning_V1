#!/bin/bash

# InULearning 系統檢查腳本
# 用於診斷系統狀態和問題

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

echo "🔍 InULearning 系統檢查"
echo "======================="

# 檢查 Docker 環境
log_info "檢查 Docker 環境..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker: $DOCKER_VERSION"
else
    log_error "Docker 未安裝"
fi

if command -v docker compose &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    log_success "Docker Compose: $COMPOSE_VERSION"
else
    log_error "Docker Compose 未安裝"
fi

# 檢查 Docker 服務狀態
if docker info &> /dev/null; then
    log_success "Docker 服務運行正常"
else
    log_error "Docker 服務未運行"
fi

echo ""

# 檢查容器狀態
log_info "檢查容器狀態..."
if docker compose ps &> /dev/null; then
    docker compose ps
else
    log_warning "無法獲取容器狀態"
fi

echo ""

# 檢查端口占用
log_info "檢查端口占用..."
PORTS=(8080 8081 8082 8083 8001 8002 8003 5432 27017 6379 9000 9001)
for port in "${PORTS[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        log_success "端口 $port 已被使用"
    else
        log_warning "端口 $port 未被使用"
    fi
done

echo ""

# 檢查服務連通性
log_info "檢查服務連通性..."
FRONTEND_PORTS=(8080 8081 8082 8083)
FRONTEND_NAMES=("學生端" "管理員端" "家長端" "教師端")

for i in "${!FRONTEND_PORTS[@]}"; do
    if curl -s -f "http://localhost:${FRONTEND_PORTS[$i]}" > /dev/null 2>&1; then
        log_success "${FRONTEND_NAMES[$i]} (http://localhost:${FRONTEND_PORTS[$i]}) 可訪問"
    else
        log_warning "${FRONTEND_NAMES[$i]} (http://localhost:${FRONTEND_PORTS[$i]}) 無法訪問"
    fi
done

echo ""

# 檢查數據庫連接
log_info "檢查數據庫連接..."
if docker compose exec -T postgres pg_isready -U aipe-tester &>/dev/null; then
    log_success "PostgreSQL 連接正常"
else
    log_warning "PostgreSQL 連接異常"
fi

if docker compose exec -T redis redis-cli ping &>/dev/null; then
    log_success "Redis 連接正常"
else
    log_warning "Redis 連接異常"
fi

if docker compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
    log_success "MongoDB 連接正常"
else
    log_warning "MongoDB 連接異常"
fi

echo ""

# 檢查日誌中的錯誤
log_info "檢查最近的錯誤日誌..."
SERVICES=("auth-service" "question-bank-service" "learning-service" "nginx")
for service in "${SERVICES[@]}"; do
    ERROR_COUNT=$(docker compose logs --tail=50 $service 2>/dev/null | grep -i error | wc -l)
    if [ $ERROR_COUNT -eq 0 ]; then
        log_success "$service: 無錯誤"
    else
        log_warning "$service: 發現 $ERROR_COUNT 條錯誤"
    fi
done

echo ""

# 檢查磁碟空間
log_info "檢查系統資源..."
if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h . | awk 'NR==2{print $5}')
    DISK_AVAIL=$(df -h . | awk 'NR==2{print $4}')
    log_info "磁碟使用率: $DISK_USAGE, 可用空間: $DISK_AVAIL"
fi

if command -v free &> /dev/null; then
    MEMORY_USAGE=$(free -h | awk 'NR==2{printf "%.1f/%.1f GB (%.1f%%)", $3/1024, $2/1024, $3*100/$2}')
    log_info "記憶體使用: $MEMORY_USAGE"
fi

echo ""

# 檢查測試帳號
log_info "檢查測試帳號..."
if docker compose exec -T postgres psql -U aipe-tester -d inulearning -c "SELECT email, role FROM users ORDER BY role;" 2>/dev/null; then
    log_success "測試帳號查詢成功"
else
    log_warning "無法查詢測試帳號"
fi

echo ""
echo "🔧 常用故障排除命令："
echo "   查看特定服務日誌: docker compose logs -f [服務名]"
echo "   重啟特定服務: docker compose restart [服務名]"
echo "   完全重新部署: ./start.sh"
echo "   快速重啟: ./restart.sh"
echo "   進入容器調試: docker compose exec [服務名] bash" 