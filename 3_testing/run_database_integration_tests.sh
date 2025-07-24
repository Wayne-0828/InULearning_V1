#!/bin/bash

# 微服務資料庫整合測試執行腳本
# 用於執行 Phase 2.3 的資料庫整合測試

set -e  # 遇到錯誤時退出

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

# 檢查 Python 環境
check_python_environment() {
    log_info "檢查 Python 環境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安裝"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1)
    log_success "Python 版本: $python_version"
    
    # 檢查必要的 Python 套件
    required_packages=("aiohttp" "asyncio" "sqlalchemy" "motor" "redis")
    missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -ne 0 ]; then
        log_warning "缺少以下 Python 套件: ${missing_packages[*]}"
        log_info "請執行: pip install ${missing_packages[*]}"
        exit 1
    fi
    
    log_success "Python 環境檢查完成"
}

# 檢查資料庫服務
check_database_services() {
    log_info "檢查資料庫服務..."
    
    # 檢查 PostgreSQL
    if ! pg_isready -h localhost -p 5432 &> /dev/null; then
        log_warning "PostgreSQL 服務未運行或無法連接"
    else
        log_success "PostgreSQL 服務正常"
    fi
    
    # 檢查 MongoDB
    if ! nc -z localhost 27017 2>/dev/null; then
        log_warning "MongoDB 服務未運行或無法連接"
    else
        log_success "MongoDB 服務正常"
    fi
    
    # 檢查 Redis
    if ! nc -z localhost 6379 2>/dev/null; then
        log_warning "Redis 服務未運行或無法連接"
    else
        log_success "Redis 服務正常"
    fi
}

# 執行資料庫整合測試
run_integration_tests() {
    log_info "執行微服務資料庫整合測試..."
    
    if [ -f "test_database_integration.py" ]; then
        python3 test_database_integration.py
        if [ $? -eq 0 ]; then
            log_success "微服務資料庫整合測試完成"
        else
            log_error "微服務資料庫整合測試失敗"
            return 1
        fi
    else
        log_error "找不到 test_database_integration.py 檔案"
        return 1
    fi
}

# 執行資料一致性檢查
run_consistency_checks() {
    log_info "執行資料庫一致性檢查..."
    
    if [ -f "test_data_consistency.py" ]; then
        python3 test_data_consistency.py
        if [ $? -eq 0 ]; then
            log_success "資料庫一致性檢查完成"
        else
            log_error "資料庫一致性檢查失敗"
            return 1
        fi
    else
        log_error "找不到 test_data_consistency.py 檔案"
        return 1
    fi
}

# 顯示測試報告
show_reports() {
    log_info "顯示測試報告..."
    
    if [ -f "database_integration_test_report.txt" ]; then
        echo ""
        echo "=" * 80
        echo "微服務資料庫整合測試報告"
        echo "=" * 80
        cat database_integration_test_report.txt
        echo ""
    fi
    
    if [ -f "data_consistency_check_report.txt" ]; then
        echo ""
        echo "=" * 80
        echo "資料庫一致性檢查報告"
        echo "=" * 80
        cat data_consistency_check_report.txt
        echo ""
    fi
}

# 清理臨時檔案
cleanup() {
    log_info "清理臨時檔案..."
    
    # 可以添加清理邏輯
    log_success "清理完成"
}

# 主函數
main() {
    echo "🚀 InULearning 微服務資料庫整合測試"
    echo "=================================="
    echo ""
    
    # 檢查環境
    check_python_environment
    check_database_services
    
    echo ""
    
    # 執行測試
    run_integration_tests
    run_consistency_checks
    
    echo ""
    
    # 顯示報告
    show_reports
    
    # 清理
    cleanup
    
    echo ""
    log_success "所有測試完成！"
    echo "請查看生成的報告檔案以了解詳細結果。"
}

# 處理命令行參數
case "${1:-}" in
    --help|-h)
        echo "用法: $0 [選項]"
        echo ""
        echo "選項:"
        echo "  --help, -h     顯示此幫助訊息"
        echo "  --check-only   只檢查環境，不執行測試"
        echo "  --integration-only  只執行整合測試"
        echo "  --consistency-only  只執行一致性檢查"
        echo ""
        echo "範例:"
        echo "  $0                    # 執行所有測試"
        echo "  $0 --check-only       # 只檢查環境"
        echo "  $0 --integration-only # 只執行整合測試"
        ;;
    --check-only)
        check_python_environment
        check_database_services
        ;;
    --integration-only)
        check_python_environment
        run_integration_tests
        show_reports
        ;;
    --consistency-only)
        check_python_environment
        run_consistency_checks
        show_reports
        ;;
    "")
        main
        ;;
    *)
        log_error "未知選項: $1"
        echo "使用 --help 查看可用選項"
        exit 1
        ;;
esac 