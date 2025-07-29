#!/bin/bash

# InULearning 階段一整合測試腳本
# 測試 API 路由統一和基礎整合功能
# 版本: v1.0.0

set -e

echo "🧪 InULearning 階段一整合測試開始..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試結果統計
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 測試函數
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    local method="${4:-GET}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "  測試 $name: "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    else
        response="000"
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ 通過${NC} (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ 失敗${NC} (期望 $expected_status, 得到 $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

echo ""
echo "📋 階段一核心測試項目:"
echo ""

# 1. 測試基礎服務健康檢查
echo "🔍 1. 基礎服務健康檢查"
test_endpoint "Nginx健康檢查" "http://localhost/health" "200"
test_endpoint "認證服務健康檢查" "http://localhost:8001/health" "200"
test_endpoint "題庫服務健康檢查" "http://localhost:8002/health" "200"
test_endpoint "學習服務健康檢查" "http://localhost:8003/health" "200"

echo ""
echo "🔍 2. API 路由統一測試"
# 測試 API 路由是否正確代理
test_endpoint "認證API路由" "http://localhost/api/v1/auth/health" "200"
test_endpoint "題庫API路由" "http://localhost/api/v1/questions/health" "200"
test_endpoint "學習API路由" "http://localhost/api/v1/learning/health" "200"

echo ""
echo "🔍 3. 前端應用訪問測試"
test_endpoint "學生前端首頁" "http://localhost:8080/" "200"
test_endpoint "學生前端登入頁" "http://localhost:8080/pages/login.html" "200"

echo ""
echo "🔍 4. 資料庫連接測試"
# 簡單的資料庫連接測試
echo -n "  測試 PostgreSQL 連接: "
if docker exec inulearning_postgres pg_isready -U aipe-tester -d inulearning >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 通過${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ 失敗${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo -n "  測試 MongoDB 連接: "
if docker exec inulearning_mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 通過${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ 失敗${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "🔍 5. 測試資料驗證"
echo -n "  測試資料庫測試資料: "
user_count=$(docker exec inulearning_postgres psql -U aipe-tester -d inulearning -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' \n' || echo "0")
if [ "$user_count" -gt "0" ]; then
    echo -e "${GREEN}✓ 通過${NC} (發現 $user_count 個用戶)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ 失敗${NC} (用戶數: $user_count)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "📊 測試結果統計:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "總測試數: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通過測試: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失敗測試: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 階段一整合測試全部通過！${NC}"
    echo ""
    echo "✅ 已完成項目:"
    echo "  • API 路由統一修復"
    echo "  • Nginx 代理配置正確"
    echo "  • 前端 API 路徑修復"
    echo "  • AI 分析功能顯示開發中"
    echo "  • 測試資料初始化完成"
    echo ""
    echo "📋 測試帳號:"
    echo "  • 學生: student01@test.com / password123"
    echo "  • 家長: parent01@test.com / password123"
    echo "  • 教師: teacher01@test.com / password123"
    echo "  • 管理員: admin01@test.com / password123"
    echo ""
    echo "🔗 訪問地址:"
    echo "  • 學生前端: http://localhost:8080"
    echo "  • API 文檔: http://localhost:8001/docs"
    echo ""
    echo -e "${GREEN}✨ 可以開始進行階段二開發！${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 階段一整合測試發現問題！${NC}"
    echo ""
    echo "請檢查以下項目:"
    echo "  • Docker 容器是否全部啟動"
    echo "  • 服務端口是否正確映射"
    echo "  • 資料庫初始化是否成功"
    echo ""
    echo "建議執行: docker-compose logs [服務名]"
    exit 1
fi 