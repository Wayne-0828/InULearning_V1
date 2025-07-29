#!/bin/bash

# InULearning Docker 啟動腳本
# 作者: AIPE01_group2
# 版本: v1.1.0

set -e

echo "🚀 正在啟動 InULearning 系統..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
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

# 錯誤處理函數
handle_error() {
    log_error "腳本執行失敗，正在清理..."
    docker compose down --remove-orphans 2>/dev/null || true
    exit 1
}

trap handle_error ERR

# 檢查系統環境
check_system() {
    log_info "檢查系統環境..."
    
    # 檢查作業系統
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "檢測到 Linux 系統"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "檢測到 macOS 系統"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        log_success "檢測到 Windows 系統 (WSL/Git Bash)"
    else
        log_warning "未知的作業系統類型: $OSTYPE"
    fi
    
    # 檢查可用記憶體
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
        if (( $(echo "$MEMORY_GB < 4.0" | bc -l) )); then
            log_warning "系統記憶體較少 (${MEMORY_GB}GB)，建議至少 4GB"
        else
            log_success "系統記憶體充足 (${MEMORY_GB}GB)"
        fi
    fi
    
    # 檢查磁碟空間
    DISK_SPACE=$(df -h . | awk 'NR==2{print $4}')
    log_info "可用磁碟空間: $DISK_SPACE"
}

# 檢查 Docker 環境
check_docker() {
    log_info "檢查 Docker 環境..."
    
    # 檢查 Docker 是否安裝
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝，請先安裝 Docker"
        echo "安裝指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 檢查 Docker 是否運行
    if ! docker info &> /dev/null; then
        log_error "Docker 服務未運行，請先啟動 Docker"
        exit 1
    fi
    
    # 檢查 Docker Compose 是否安裝
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose 未安裝，請先安裝 Docker Compose"
        echo "安裝指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # 檢查 Docker 版本
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    COMPOSE_VERSION=$(docker compose version --short)
    log_success "Docker 版本: $DOCKER_VERSION"
    log_success "Docker Compose 版本: $COMPOSE_VERSION"
    
    # 檢查 Docker 權限
    if ! docker ps &> /dev/null; then
        log_warning "當前用戶可能沒有 Docker 權限，嘗試使用 sudo..."
        if ! sudo docker ps &> /dev/null; then
            log_error "無法訪問 Docker，請檢查權限設置"
            exit 1
        fi
    fi
}

# 清理舊環境
cleanup_old_environment() {
    log_info "清理舊環境..."
    
    # 停止並移除舊容器
    docker compose down --remove-orphans --volumes 2>/dev/null || true
    
    # 清理未使用的 Docker 資源
    log_info "清理未使用的 Docker 資源..."
    docker system prune -f --volumes 2>/dev/null || true
    
    log_success "舊環境清理完成"
}

# 建立必要的目錄和檔案
setup_directories() {
    log_info "建立必要的目錄和檔案..."
    
    # 建立目錄
    mkdir -p logs
    mkdir -p init-scripts
    mkdir -p nginx/conf.d
    mkdir -p data/postgres
    mkdir -p data/mongodb
    mkdir -p data/redis
    mkdir -p data/minio
    
    # 設置權限
    chmod 755 logs init-scripts nginx/conf.d
    
    log_success "目錄結構建立完成"
}

# 檢查和建立環境變數檔案
setup_environment() {
    log_info "檢查環境變數檔案..."
    
    if [ ! -f .env ]; then
        if [ -f env.docker ]; then
            log_info "建立 .env 檔案..."
            cp env.docker .env
            log_success ".env 檔案已建立"
        else
            log_warning "env.docker 檔案不存在，建立預設 .env 檔案..."
            cat > .env << EOF
# Database Configuration
POSTGRES_DB=inulearning
POSTGRES_USER=aipe-tester
POSTGRES_PASSWORD=aipe-tester
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MongoDB Configuration
MONGODB_DATABASE=inulearning
MONGODB_USERNAME=aipe-tester
MONGODB_PASSWORD=aipe-tester
MONGODB_HOST=mongodb
MONGODB_PORT=27017

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=aipe-tester

# MinIO Configuration
MINIO_ROOT_USER=aipe-tester
MINIO_ROOT_PASSWORD=aipe-tester
MINIO_HOST=minio
MINIO_PORT=9000

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=true
ENVIRONMENT=development
EOF
            log_success "預設 .env 檔案已建立"
        fi
    else
        log_success ".env 檔案已存在"
    fi
}

# 建立並啟動服務
start_services() {
    log_info "建立並啟動容器..."
    
    # 拉取最新映像
    log_info "拉取基礎映像..."
    docker compose pull --ignore-pull-failures 2>/dev/null || true
    
    # 建立並啟動服務
    docker compose up --build -d
    
    log_success "容器啟動完成"
}

# 等待服務就緒
wait_for_services() {
    log_info "等待服務啟動..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        
        # 檢查基礎服務
        if docker compose exec -T postgres pg_isready -U aipe-tester &>/dev/null && \
           docker compose exec -T redis redis-cli ping &>/dev/null; then
            log_success "基礎服務已就緒"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "服務啟動超時"
            return 1
        fi
        
        echo -n "."
        sleep 2
    done
    
    # 額外等待應用服務
    log_info "等待應用服務初始化..."
    sleep 15
}

# 檢查服務健康狀態
check_service_health() {
    log_info "檢查服務健康狀態..."
    
    local services=("postgres" "mongodb" "redis" "minio" "auth-service" "question-bank-service" "learning-service" "nginx")
    local frontend_services=("student-frontend" "admin-frontend" "teacher-frontend" "parent-frontend")
    
    # 檢查後端服務
    for service in "${services[@]}"; do
        if docker compose ps $service | grep -q "Up"; then
            log_success "$service 運行正常"
        else
            log_warning "$service 狀態異常，檢查日誌: docker compose logs $service"
        fi
    done
    
    # 檢查前端服務
    for service in "${frontend_services[@]}"; do
        if docker compose ps $service | grep -q "Up"; then
            log_success "$service 運行正常"
        else
            log_warning "$service 狀態異常"
        fi
    done
}

# 測試服務連通性
test_connectivity() {
    log_info "測試服務連通性..."
    
    # 測試前端訪問
    local ports=("8080" "8081" "8082" "8083")
    local names=("學生端" "管理員端" "家長端" "教師端")
    
    for i in "${!ports[@]}"; do
        if curl -s -f "http://localhost:${ports[$i]}" > /dev/null; then
            log_success "${names[$i]} (http://localhost:${ports[$i]}) 可訪問"
        else
            log_warning "${names[$i]} (http://localhost:${ports[$i]}) 暫時無法訪問"
        fi
    done
    
    # 測試 API Gateway
    if curl -s -f "http://localhost:80/health" > /dev/null 2>&1; then
        log_success "API Gateway 運行正常"
    else
        log_warning "API Gateway 可能需要更多時間啟動"
    fi
}

# 初始化測試資料
initialize_test_data() {
    log_info "初始化測試資料..."
    
    # 等待資料庫完全就緒
    sleep 5
    
    # 檢查是否需要初始化
    if docker compose exec -T postgres psql -U aipe-tester -d inulearning -c "SELECT COUNT(*) FROM users;" 2>/dev/null | grep -q "0"; then
        log_info "初始化測試用戶..."
        
        # 創建測試用戶（如果不存在）
        docker compose exec -T postgres psql -U aipe-tester -d inulearning -c "
        INSERT INTO users (username, email, hashed_password, role, first_name, last_name, is_active, is_verified, created_at) VALUES 
        ('student01', 'student01@test.com', '\$2b\$12\$I7PCkeIs6YA.vxxsMr5ch.BzDX7otv0MvxQw3DrPWmL8WpDa0M7Qm', 'student', '學生', '01', true, true, NOW()),
        ('teacher01', 'teacher01@test.com', '\$2b\$12\$I7PCkeIs6YA.vxxsMr5ch.BzDX7otv0MvxQw3DrPWmL8WpDa0M7Qm', 'teacher', '教師', '01', true, true, NOW()),
        ('parent01', 'parent01@test.com', '\$2b\$12\$I7PCkeIs6YA.vxxsMr5ch.BzDX7otv0MvxQw3DrPWmL8WpDa0M7Qm', 'parent', '家長', '01', true, true, NOW()),
        ('admin01', 'admin01@test.com', '\$2b\$12\$I7PCkeIs6YA.vxxsMr5ch.BzDX7otv0MvxQw3DrPWmL8WpDa0M7Qm', 'admin', '管理員', '01', true, true, NOW())
        ON CONFLICT (email) DO NOTHING;
        " 2>/dev/null || log_warning "測試用戶可能已存在"
        
        log_success "測試資料初始化完成"
    else
        log_success "測試資料已存在"
    fi
}

# 顯示系統資訊
show_system_info() {
    echo ""
    echo "🎉 InULearning 系統啟動完成！"
    echo ""
    echo "📋 服務訪問地址："
    echo "   🎓 學生端前端: http://localhost:8080"
    echo "   👨‍💼 管理員端前端: http://localhost:8081"
    echo "   👪 家長端前端: http://localhost:8082"
    echo "   👨‍🏫 教師端前端: http://localhost:8083"
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
    echo "   進入容器: docker compose exec [服務名] bash"
    echo ""
    echo "📝 測試帳號 (密碼都是 password123)："
    echo "   👨‍🎓 學生帳號: student01@test.com"
    echo "   👨‍🏫 教師帳號: teacher01@test.com"
    echo "   👪 家長帳號: parent01@test.com"
    echo "   👨‍💼 管理員帳號: admin01@test.com"
    echo ""
    echo "🔍 故障排除："
    echo "   如果服務無法訪問，請等待 1-2 分鐘後重試"
    echo "   如果仍有問題，請查看日誌: docker compose logs -f"
    echo "   重新啟動: ./start.sh"
    echo ""
    echo "✨ 開始使用 InULearning 吧！"
}

# 主執行流程
main() {
    echo "🚀 InULearning 一鍵啟動腳本 v1.1.0"
    echo "================================================"
    
    check_system
    check_docker
    cleanup_old_environment
    setup_directories
    setup_environment
    start_services
    wait_for_services
    check_service_health
    initialize_test_data
    test_connectivity
    show_system_info
    
    log_success "啟動流程完成！"
}

# 執行主函數
main "$@" 