#!/bin/bash

# =============================================================================
# InULearning 個人化學習平台 - 開發環境設置腳本
# =============================================================================
# 此腳本用於快速設置開發環境

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查前置需求
check_prerequisites() {
    log_info "檢查前置需求..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝，請先安裝 Docker"
        exit 1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安裝，請先安裝 Docker Compose"
        exit 1
    fi
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安裝，請先安裝 Python 3"
        exit 1
    fi
    
    log_success "前置需求檢查完成"
}

# 設置環境變數
setup_environment() {
    log_info "設置環境變數..."
    
    # 檢查 .env 檔案是否存在
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            log_info "複製環境變數範本..."
            cp env.example .env
            log_warning "請編輯 .env 檔案，填入實際的配置值"
        else
            log_error "找不到 env.example 檔案"
            exit 1
        fi
    else
        log_info ".env 檔案已存在"
    fi
    
    log_success "環境變數設置完成"
}

# 建立必要的目錄
create_directories() {
    log_info "建立必要的目錄..."
    
    # 建立日誌目錄
    mkdir -p logs
    
    # 建立資料目錄
    mkdir -p data/{postgresql,mongodb,redis,milvus,minio}
    
    # 建立快取目錄
    mkdir -p cache
    
    # 建立臨時檔案目錄
    mkdir -p tmp
    
    log_success "目錄建立完成"
}

# 設置 Docker 權限
setup_docker_permissions() {
    log_info "設置 Docker 權限..."
    
    # 確保當前用戶在 docker 群組中
    if ! groups $USER | grep -q docker; then
        log_warning "當前用戶不在 docker 群組中，請執行以下命令："
        echo "sudo usermod -aG docker $USER"
        echo "然後重新登入或執行：newgrp docker"
    fi
    
    log_success "Docker 權限設置完成"
}

# 啟動基礎服務
start_base_services() {
    log_info "啟動基礎服務..."
    
    # 檢查 Docker Compose 檔案是否存在
    if [ ! -f "4_deployment/docker/docker-compose.dev.yml" ]; then
        log_error "找不到 docker-compose.dev.yml 檔案"
        exit 1
    fi
    
    # 啟動基礎服務（資料庫、快取等）
    docker-compose -f 4_deployment/docker/docker-compose.dev.yml up -d postgresql mongodb redis milvus minio rabbitmq
    
    # 等待服務啟動
    log_info "等待服務啟動..."
    sleep 10
    
    # 檢查服務狀態
    docker-compose -f 4_deployment/docker/docker-compose.dev.yml ps
    
    log_success "基礎服務啟動完成"
}

# 初始化資料庫
initialize_databases() {
    log_info "初始化資料庫..."
    
    # 等待 PostgreSQL 完全啟動
    log_info "等待 PostgreSQL 啟動..."
    until docker-compose -f 4_deployment/docker/docker-compose.dev.yml exec -T postgresql pg_isready -U inulearning_user; do
        sleep 2
    done
    
    # 執行資料庫遷移（如果存在）
    if [ -f "2_implementation/database/migrations/postgresql/init.sql" ]; then
        log_info "執行 PostgreSQL 初始化腳本..."
        docker-compose -f 4_deployment/docker/docker-compose.dev.yml exec -T postgresql psql -U inulearning_user -d inulearning -f /docker-entrypoint-initdb.d/init.sql
    fi
    
    # 等待 MongoDB 完全啟動
    log_info "等待 MongoDB 啟動..."
    until docker-compose -f 4_deployment/docker/docker-compose.dev.yml exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
        sleep 2
    done
    
    # 執行 MongoDB 初始化腳本（如果存在）
    if [ -f "2_implementation/database/migrations/mongodb/init-mongo.js" ]; then
        log_info "執行 MongoDB 初始化腳本..."
        docker-compose -f 4_deployment/docker/docker-compose.dev.yml exec -T mongodb mongosh --file /docker-entrypoint-initdb.d/init-mongo.js
    fi
    
    log_success "資料庫初始化完成"
}

# 安裝 Python 依賴
install_python_dependencies() {
    log_info "安裝 Python 依賴..."
    
    # 檢查虛擬環境
    if [ ! -d "venv" ]; then
        log_info "建立 Python 虛擬環境..."
        python3 -m venv venv
    fi
    
    # 啟動虛擬環境
    source venv/bin/activate
    
    # 升級 pip
    pip install --upgrade pip
    
    # 安裝依賴
    pip install -r requirements.txt
    
    log_success "Python 依賴安裝完成"
}

# 設置開發工具
setup_development_tools() {
    log_info "設置開發工具..."
    
    # 設置 Git hooks（如果存在）
    if [ -d ".git/hooks" ]; then
        log_info "設置 Git hooks..."
        # 這裡可以添加自定義的 Git hooks
    fi
    
    # 設置程式碼格式化工具
    log_info "設置程式碼格式化工具..."
    # 這裡可以添加 Black、Flake8 等工具的配置
    
    log_success "開發工具設置完成"
}

# 顯示完成訊息
show_completion_message() {
    echo ""
    echo "=========================================="
    echo "🎉 開發環境設置完成！"
    echo "=========================================="
    echo ""
    echo "📋 下一步操作："
    echo "1. 編輯 .env 檔案，填入實際的配置值"
    echo "2. 啟動所有服務："
    echo "   docker-compose -f 4_deployment/docker/docker-compose.dev.yml up -d"
    echo ""
    echo "🌐 服務訪問地址："
    echo "- API Gateway: http://localhost:8000"
    echo "- 學生端應用: http://localhost:3000"
    echo "- 家長端應用: http://localhost:3001"
    echo "- 教師端應用: http://localhost:3002"
    echo "- API 文檔: http://localhost:8000/docs"
    echo ""
    echo "📚 相關文檔："
    echo "- 開發指南: docs/development/getting_started.md"
    echo "- API 文檔: docs/api/"
    echo "- 部署指南: docs/deployment/"
    echo ""
    echo "🔧 常用命令："
    echo "- 查看服務狀態: docker-compose ps"
    echo "- 查看服務日誌: docker-compose logs -f"
    echo "- 停止所有服務: docker-compose down"
    echo ""
}

# 主函數
main() {
    echo "=========================================="
    echo "🚀 InULearning 開發環境設置"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    setup_environment
    create_directories
    setup_docker_permissions
    start_base_services
    initialize_databases
    install_python_dependencies
    setup_development_tools
    
    show_completion_message
}

# 執行主函數
main "$@" 