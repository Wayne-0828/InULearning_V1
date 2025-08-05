#!/bin/bash

# InULearning 學習歷程功能測試腳本
# 測試新開發的學習記錄提交和查詢功能

set -e

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

log_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

# 全局變量
BASE_URL="http://localhost"
LEARNING_SERVICE_URL="http://localhost:8003"
AUTH_TOKEN=""
USER_ID=""

# 測試用戶登入
test_login() {
    log_step "測試用戶登入..."
    
    local response=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "student01@test.com",
            "password": "password123"
        }')
    
    if echo "$response" | grep -q "access_token"; then
        AUTH_TOKEN=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
        # 從JWT Token中解析用戶ID
        USER_ID="3"  # 暫時硬編碼，因為響應中沒有user對象
        
        if [ -n "$AUTH_TOKEN" ]; then
            log_success "用戶登入成功，獲得Token"
            return 0
        fi
    fi
    
    log_error "用戶登入失敗"
    return 1
}

# 測試提交練習結果
test_submit_exercise() {
    log_step "測試提交練習結果..."
    
    local response=$(curl -s -X POST "$LEARNING_SERVICE_URL/api/v1/learning/exercises/complete" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d '{
            "session_name": "數學練習 - 一元一次方程式測試",
            "subject": "數學",
            "grade": "8A",
            "chapter": "一元一次方程式",
            "publisher": "南一",
            "difficulty": "normal",
            "knowledge_points": ["一元一次方程式", "移項運算"],
            "exercise_results": [
                {
                    "question_id": "test_q_001",
                    "subject": "數學",
                    "grade": "8A",
                    "chapter": "一元一次方程式",
                    "publisher": "南一",
                    "knowledge_points": ["一元一次方程式"],
                    "question_content": "解方程式 2x + 3 = 7",
                    "answer_choices": {"A": "x = 2", "B": "x = 3", "C": "x = 4", "D": "x = 5"},
                    "difficulty": "normal",
                    "question_topic": "一元一次方程式解法",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": true,
                    "score": 100.0,
                    "explanation": "移項得到 2x = 4，所以 x = 2",
                    "time_spent": 45
                },
                {
                    "question_id": "test_q_002",
                    "subject": "數學",
                    "grade": "8A",
                    "chapter": "一元一次方程式",
                    "publisher": "南一",
                    "knowledge_points": ["移項運算"],
                    "question_content": "解方程式 3x - 5 = 10",
                    "answer_choices": {"A": "x = 5", "B": "x = 4", "C": "x = 3", "D": "x = 2"},
                    "difficulty": "normal",
                    "question_topic": "移項運算練習",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": true,
                    "score": 100.0,
                    "explanation": "移項得到 3x = 15，所以 x = 5",
                    "time_spent": 30
                }
            ],
            "total_time_spent": 300,
            "session_metadata": {"source": "test", "device": "script"}
        }')
    
    if echo "$response" | grep -q "session_id"; then
        log_success "練習結果提交成功"
        SESSION_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null || echo "")
        log_info "會話ID: $SESSION_ID"
        return 0
    else
        log_error "練習結果提交失敗"
        log_error "響應: $response"
        return 1
    fi
}

# 測試查詢學習記錄
test_get_records() {
    log_step "測試查詢學習記錄..."
    
    local response=$(curl -s -X GET "$LEARNING_SERVICE_URL/api/v1/learning/records?page=1&page_size=10" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    
    if echo "$response" | grep -q "sessions"; then
        local total=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
        log_success "學習記錄查詢成功，共 $total 筆記錄"
        return 0
    else
        log_error "學習記錄查詢失敗"
        log_error "響應: $response"
        return 1
    fi
}

# 測試查詢學習統計
test_get_statistics() {
    log_step "測試查詢學習統計..."
    
    local response=$(curl -s -X GET "$LEARNING_SERVICE_URL/api/v1/learning/statistics" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    
    if echo "$response" | grep -q "total_sessions"; then
        local sessions=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_sessions'])" 2>/dev/null || echo "0")
        local questions=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_questions'])" 2>/dev/null || echo "0")
        local accuracy=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['overall_accuracy'])" 2>/dev/null || echo "0")
        log_success "學習統計查詢成功"
        log_info "總會話數: $sessions"
        log_info "總題目數: $questions"
        log_info "整體正確率: $accuracy%"
        return 0
    else
        log_error "學習統計查詢失敗"
        log_error "響應: $response"
        return 1
    fi
}

# 測試查詢會話詳情
test_get_session_detail() {
    log_step "測試查詢會話詳情..."
    
    if [ -z "$SESSION_ID" ]; then
        log_warning "沒有會話ID，跳過詳情測試"
        return 0
    fi
    
    local response=$(curl -s -X GET "$LEARNING_SERVICE_URL/api/v1/learning/records/$SESSION_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    
    if echo "$response" | grep -q "session"; then
        local record_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['exercise_records']))" 2>/dev/null || echo "0")
        log_success "會話詳情查詢成功，包含 $record_count 筆練習記錄"
        return 0
    else
        log_error "會話詳情查詢失敗"
        log_error "響應: $response"
        return 1
    fi
}

# 測試篩選功能
test_filter_records() {
    log_step "測試記錄篩選功能..."
    
    # 測試科目篩選
    local response=$(curl -s -X GET "$LEARNING_SERVICE_URL/api/v1/learning/records?subject=數學&page=1&page_size=5" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    
    if echo "$response" | grep -q "sessions"; then
        local total=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
        log_success "科目篩選測試成功，數學科目共 $total 筆記錄"
    else
        log_error "科目篩選測試失敗"
        return 1
    fi
    
    # 測試年級篩選
    local response2=$(curl -s -X GET "$LEARNING_SERVICE_URL/api/v1/learning/records?grade=8A&page=1&page_size=5" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    
    if echo "$response2" | grep -q "sessions"; then
        local total2=$(echo "$response2" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
        log_success "年級篩選測試成功，8A年級共 $total2 筆記錄"
        return 0
    else
        log_error "年級篩選測試失敗"
        return 1
    fi
}

# 檢查服務狀態
check_services() {
    log_step "檢查服務狀態..."
    
    # 檢查學習服務健康狀態
    if curl -s -f "$BASE_URL/api/v1/learning/health" > /dev/null; then
        log_success "學習服務運行正常"
    else
        log_error "學習服務無法訪問"
        return 1
    fi
    
    # 檢查認證服務
    if curl -s -f "$BASE_URL/api/v1/auth/health" > /dev/null; then
        log_success "認證服務運行正常"
    else
        log_error "認證服務無法訪問"
        return 1
    fi
    
    return 0
}

# 主測試流程
main() {
    echo "🧪 InULearning 學習歷程功能測試"
    echo "=================================="
    echo ""
    
    # 檢查依賴
    if ! command -v python3 &> /dev/null; then
        log_warning "Python3 未安裝，部分解析功能可能無法使用"
    fi
    
    # 檢查服務狀態
    if ! check_services; then
        log_error "服務狀態檢查失敗，請確保系統已啟動"
        exit 1
    fi
    
    # 執行測試
    local failed_tests=0
    
    # 1. 用戶登入測試
    if ! test_login; then
        ((failed_tests++))
    fi
    
    if [ -n "$AUTH_TOKEN" ]; then
        # 2. 提交練習結果測試
        if ! test_submit_exercise; then
            ((failed_tests++))
        fi
        
        # 等待數據處理
        sleep 2
        
        # 3. 查詢學習記錄測試
        if ! test_get_records; then
            ((failed_tests++))
        fi
        
        # 4. 查詢學習統計測試
        if ! test_get_statistics; then
            ((failed_tests++))
        fi
        
        # 5. 查詢會話詳情測試
        if ! test_get_session_detail; then
            ((failed_tests++))
        fi
        
        # 6. 篩選功能測試
        if ! test_filter_records; then
            ((failed_tests++))
        fi
    else
        log_error "無法獲得認證Token，跳過後續測試"
        ((failed_tests+=5))
    fi
    
    # 測試結果
    echo ""
    echo "=================================="
    if [ $failed_tests -eq 0 ]; then
        log_success "🎉 所有測試通過！學習歷程功能運行正常"
    else
        log_error "❌ $failed_tests 個測試失敗"
        echo ""
        log_info "故障排除建議："
        log_info "1. 確保系統已完全啟動：./start.sh"
        log_info "2. 檢查服務日誌：docker-compose logs -f learning-service"
        log_info "3. 檢查資料庫連接：docker-compose exec postgres psql -U aipe-tester -d inulearning"
        exit 1
    fi
    
    echo ""
    log_info "💡 前端測試建議："
    log_info "1. 訪問學生端：http://localhost:8080"
    log_info "2. 使用測試帳號登入：student01@test.com / password123"
    log_info "3. 進入學習歷程頁面查看記錄"
    log_info "4. 測試篩選和詳情查看功能"
}

# 檢查是否為直接執行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi