#!/bin/bash

# =============================================================================
# InULearning 服務測試腳本
# =============================================================================

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：打印帶顏色的訊息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函數：檢查服務是否運行
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    print_status "檢查 $service_name 服務..."
    
    if curl -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        print_success "$service_name 服務運行正常 (端口: $port)"
        return 0
    else
        print_error "$service_name 服務無法連接 (端口: $port)"
        return 1
    fi
}

# 函數：檢查資料庫連接
check_database() {
    local db_name=$1
    local port=$2
    
    print_status "檢查 $db_name 資料庫..."
    
    case $db_name in
        "PostgreSQL")
            if docker exec inulearning_postgresql_test pg_isready -U aipe-tester -d inulearning_test > /dev/null 2>&1; then
                print_success "PostgreSQL 資料庫連接正常"
                return 0
            else
                print_error "PostgreSQL 資料庫連接失敗"
                return 1
            fi
            ;;
        "MongoDB")
            if docker exec inulearning_mongodb_test mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1; then
                print_success "MongoDB 資料庫連接正常"
                return 0
            else
                print_error "MongoDB 資料庫連接失敗"
                return 1
            fi
            ;;
        "Redis")
            if docker exec inulearning_redis_test redis-cli -a redis_password ping > /dev/null 2>&1; then
                print_success "Redis 資料庫連接正常"
                return 0
            else
                print_error "Redis 資料庫連接失敗"
                return 1
            fi
            ;;
    esac
}

# 主函數
main() {
    echo "=============================================================================="
    echo "🐳 InULearning 服務測試腳本"
    echo "=============================================================================="
    
    # 檢查 Docker 是否運行
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker 未運行，請先啟動 Docker"
        exit 1
    fi
    
    # 檢查 Docker Compose 檔案是否存在
    if [ ! -f "docker-compose.test.yml" ]; then
        print_error "找不到 docker-compose.test.yml 檔案"
        exit 1
    fi
    
    # 啟動測試環境
    print_status "啟動測試環境..."
    docker compose -f docker-compose.test.yml up -d
    
    # 等待服務啟動
    print_status "等待服務啟動 (30秒)..."
    sleep 30
    
    # 檢查資料庫服務
    echo ""
    echo "=============================================================================="
    echo "📊 檢查資料庫服務"
    echo "=============================================================================="
    
    check_database "PostgreSQL" 5432
    check_database "MongoDB" 27017
    check_database "Redis" 6379
    
    # 檢查其他服務
    echo ""
    echo "=============================================================================="
    echo "🌐 檢查其他服務"
    echo "=============================================================================="
    
    # 檢查 MinIO
    if curl -s "http://localhost:9001" > /dev/null 2>&1; then
        print_success "MinIO 服務運行正常 (端口: 9001)"
    else
        print_error "MinIO 服務無法連接 (端口: 9001)"
    fi
    
    # 檢查 Milvus
    if curl -s "http://localhost:9091/healthz" > /dev/null 2>&1; then
        print_success "Milvus 服務運行正常 (端口: 9091)"
    else
        print_error "Milvus 服務無法連接 (端口: 9091)"
    fi
    
    echo ""
    echo "=============================================================================="
    echo "🎯 測試結果摘要"
    echo "=============================================================================="
    
    print_status "測試環境已啟動，您可以開始測試您的後端服務："
    echo ""
    print_status "1. 啟動您的後端服務："
    echo "   cd ../../2_implementation"
    echo "   source venv/bin/activate"
    echo "   ./start_services.sh"
    echo ""
    print_status "2. 測試 API 端點："
    echo "   - 認證服務: http://localhost:8000/docs"
    echo "   - 學習服務: http://localhost:8001/docs"
    echo "   - 題庫服務: http://localhost:8002/docs"
    echo "   - AI 分析服務: http://localhost:8004/docs"
    echo ""
    print_status "3. 資料庫管理工具："
    echo "   - MinIO Console: http://localhost:9001"
    echo "   - PostgreSQL: localhost:5432"
    echo "   - MongoDB: localhost:27017"
    echo "   - Redis: localhost:6379"
    echo ""
    print_warning "請確保在 .env 檔案中設定正確的 GEMINI_API_KEY"
    echo ""
    print_status "停止測試環境："
    echo "   docker compose -f docker-compose.test.yml down"
}

# 執行主函數
main "$@" 