#!/bin/bash

# ===============================================
# InULearning 資料庫設置腳本
# 版本: v1.0.0
# 作者: AIPE01_group2
# 日期: 2024-12-19
# 
# 目的: 自動化設置 InULearning 學習系統資料庫
# 支援: PostgreSQL 和 MongoDB 的初始化
# ===============================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置變數
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DATABASE_DIR")")"

# 資料庫連接配置
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-inulearning}"
POSTGRES_USER="${POSTGRES_USER:-aipe-tester}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-aipe-tester}"

MONGODB_HOST="${MONGODB_HOST:-localhost}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_DB="${MONGODB_DB:-inulearning}"

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

log_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

log_highlight() {
    echo -e "${CYAN}🎯 $1${NC}"
}

# 檢查 PostgreSQL 連接
check_postgres_connection() {
    log_step "檢查 PostgreSQL 連接..."
    
    if command -v psql &> /dev/null; then
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &> /dev/null; then
            log_success "PostgreSQL 連接成功"
            return 0
        else
            log_error "無法連接到 PostgreSQL"
            return 1
        fi
    else
        log_error "psql 命令未找到，請安裝 PostgreSQL 客戶端"
        return 1
    fi
}

# 檢查 MongoDB 連接
check_mongodb_connection() {
    log_step "檢查 MongoDB 連接..."
    
    if command -v mongosh &> /dev/null; then
        if mongosh --host "$MONGODB_HOST:$MONGODB_PORT" --eval "db.runCommand('ping')" &> /dev/null; then
            log_success "MongoDB 連接成功"
            return 0
        else
            log_error "無法連接到 MongoDB"
            return 1
        fi
    elif command -v mongo &> /dev/null; then
        if mongo --host "$MONGODB_HOST:$MONGODB_PORT" --eval "db.runCommand('ping')" &> /dev/null; then
            log_success "MongoDB 連接成功"
            return 0
        else
            log_error "無法連接到 MongoDB"
            return 1
        fi
    else
        log_warning "MongoDB 客戶端未找到，跳過 MongoDB 設置"
        return 1
    fi
}

# 執行 PostgreSQL 遷移
run_postgres_migrations() {
    log_step "執行 PostgreSQL 資料庫遷移..."
    
    local migration_dir="$DATABASE_DIR/migrations/postgresql"
    
    if [ ! -d "$migration_dir" ]; then
        log_error "PostgreSQL 遷移目錄不存在: $migration_dir"
        return 1
    fi
    
    # 按順序執行遷移檔案
    for migration_file in "$migration_dir"/*.sql; do
        if [ -f "$migration_file" ]; then
            local filename=$(basename "$migration_file")
            log_info "執行遷移: $filename"
            
            if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$migration_file"; then
                log_success "遷移完成: $filename"
            else
                log_error "遷移失敗: $filename"
                return 1
            fi
        fi
    done
    
    log_success "PostgreSQL 遷移完成"
}

# 執行 PostgreSQL 種子數據
run_postgres_seeds() {
    log_step "插入 PostgreSQL 種子數據..."
    
    local seed_dir="$DATABASE_DIR/seeds/postgresql"
    
    if [ ! -d "$seed_dir" ]; then
        log_warning "PostgreSQL 種子數據目錄不存在: $seed_dir"
        return 0
    fi
    
    # 按順序執行種子檔案
    for seed_file in "$seed_dir"/*.sql; do
        if [ -f "$seed_file" ]; then
            local filename=$(basename "$seed_file")
            log_info "插入種子數據: $filename"
            
            if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$seed_file"; then
                log_success "種子數據完成: $filename"
            else
                log_warning "種子數據失敗: $filename (可能已存在)"
            fi
        fi
    done
    
    log_success "PostgreSQL 種子數據插入完成"
}

# 執行 MongoDB 設置
run_mongodb_setup() {
    log_step "設置 MongoDB..."
    
    local mongodb_dir="$DATABASE_DIR/migrations/mongodb"
    
    if [ ! -d "$mongodb_dir" ]; then
        log_warning "MongoDB 遷移目錄不存在: $mongodb_dir，跳過 MongoDB 設置"
        return 0
    fi
    
    # 執行 MongoDB 初始化腳本
    for script_file in "$mongodb_dir"/*.js; do
        if [ -f "$script_file" ]; then
            local filename=$(basename "$script_file")
            log_info "執行 MongoDB 腳本: $filename"
            
            if command -v mongosh &> /dev/null; then
                if mongosh --host "$MONGODB_HOST:$MONGODB_PORT" "$MONGODB_DB" "$script_file"; then
                    log_success "MongoDB 腳本完成: $filename"
                else
                    log_warning "MongoDB 腳本失敗: $filename"
                fi
            elif command -v mongo &> /dev/null; then
                if mongo --host "$MONGODB_HOST:$MONGODB_PORT" "$MONGODB_DB" "$script_file"; then
                    log_success "MongoDB 腳本完成: $filename"
                else
                    log_warning "MongoDB 腳本失敗: $filename"
                fi
            fi
        fi
    done
    
    log_success "MongoDB 設置完成"
}

# 驗證資料庫設置
verify_database_setup() {
    log_step "驗證資料庫設置..."
    
    # 驗證 PostgreSQL 表
    local table_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [ "$table_count" -gt "5" ]; then
        log_success "PostgreSQL 表創建成功 ($table_count 個表)"
    else
        log_warning "PostgreSQL 表創建可能有問題 (只有 $table_count 個表)"
    fi
    
    # 驗證知識點數據
    local knowledge_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM knowledge_points_master;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [ "$knowledge_count" -gt "0" ]; then
        log_success "知識點數據插入成功 ($knowledge_count 個知識點)"
    else
        log_warning "知識點數據可能未正確插入"
    fi
}

# 顯示資料庫資訊
show_database_info() {
    echo ""
    log_highlight "🎉 InULearning 資料庫設置完成！"
    echo "================================================"
    echo ""
    log_highlight "📊 資料庫連接資訊："
    echo "  PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
    echo "  用戶: $POSTGRES_USER"
    echo "  MongoDB: $MONGODB_HOST:$MONGODB_PORT/$MONGODB_DB"
    echo ""
    log_highlight "🗄️ 主要表結構："
    echo "  ✅ users - 用戶管理"
    echo "  ✅ learning_sessions - 學習會話"
    echo "  ✅ exercise_records - 練習記錄"
    echo "  ✅ user_learning_profiles - 用戶學習檔案"
    echo "  ✅ knowledge_points_master - 知識點主表"
    echo ""
    log_highlight "🎯 核心功能："
    echo "  ✅ 知識點追蹤系統"
    echo "  ✅ 用戶學習檔案管理"
    echo "  ✅ 詳細練習記錄"
    echo "  ✅ 高效能索引設計"
    echo ""
    log_highlight "🔧 管理命令："
    echo "  查看表結構: psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c '\\dt'"
    echo "  查看知識點: psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c 'SELECT * FROM knowledge_points_master LIMIT 10;'"
    echo ""
    echo "================================================"
}

# 主執行函數
main() {
    echo "🚀 InULearning 資料庫設置腳本 v1.0.0"
    echo "================================================"
    echo ""
    
    log_info "開始設置 InULearning 學習系統資料庫..."
    echo ""
    
    # 檢查連接
    if ! check_postgres_connection; then
        log_error "PostgreSQL 連接失敗，請檢查服務和配置"
        exit 1
    fi
    
    check_mongodb_connection || log_warning "MongoDB 連接失敗，將跳過 MongoDB 設置"
    
    # 執行遷移和設置
    run_postgres_migrations
    run_postgres_seeds
    run_mongodb_setup
    
    # 驗證設置
    verify_database_setup
    
    # 顯示完成資訊
    show_database_info
    
    log_success "🎉 資料庫設置完成！"
}

# 檢查是否為直接執行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi