#!/bin/bash

# =============================================================================
# InULearning 服務啟動腳本
# =============================================================================

# 設定顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查虛擬環境是否啟動
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}啟動虛擬環境...${NC}"
    source venv/bin/activate
fi

echo -e "${GREEN}InULearning 服務啟動腳本${NC}"
echo "=================================="

# 函數：啟動服務
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    
    echo -e "${BLUE}啟動 $service_name (Port: $port)...${NC}"
    cd "$service_path"
    
    # 使用 screen 在背景啟動服務
    screen -dmS "$service_name" bash -c "source ../../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port $port --reload"
    
    echo -e "${GREEN}✓ $service_name 已啟動${NC}"
    cd - > /dev/null
}

# 函數：啟動學習服務
start_learning_service() {
    local service_name="learning-service"
    local service_path="backend/learning-service"
    local port=8002
    
    echo -e "${BLUE}啟動 $service_name (Port: $port)...${NC}"
    cd "$service_path"
    
    # 使用 screen 在背景啟動服務
    screen -dmS "$service_name" bash -c "source ../../venv/bin/activate && python run.py"
    
    echo -e "${GREEN}✓ $service_name 已啟動${NC}"
    cd - > /dev/null
}

# 函數：啟動 AI 分析服務
start_ai_analysis_service() {
    echo "🚀 Starting AI Analysis Service..."
    
    # 檢查服務是否已經運行
    if screen -list | grep -q "ai-analysis-service"; then
        echo "⚠️  AI Analysis Service is already running"
        return
    fi
    
    # 啟動 AI 分析服務（使用 Poetry 環境）
    cd backend/ai-analysis-service
    screen -dmS ai-analysis-service bash -c "source /home/bheadwei/.cache/pypoetry/virtualenvs/inulearning-v1-WliJQHGv-py3.12/bin/activate && python run.py"
    
    # 等待服務啟動
    sleep 3
    
    # 檢查服務狀態
    if curl -s http://localhost:8004/health > /dev/null; then
        echo "✅ AI Analysis Service started successfully"
    else
        echo "⚠️  AI Analysis Service started but health check failed"
    fi
    
    cd ../..
}

# 檢查 screen 是否安裝
if ! command -v screen &> /dev/null; then
    echo -e "${YELLOW}安裝 screen...${NC}"
    sudo apt update && sudo apt install screen -y
fi

# 啟動所有服務
echo -e "${YELLOW}正在啟動所有服務...${NC}"

# 啟動認證服務
start_service "auth-service" "backend/auth-service" 8001

# 啟動學習服務
start_learning_service

# 啟動題庫服務
start_service "question-bank-service" "backend/question-bank-service" 8003

# 啟動 AI 分析服務
start_ai_analysis_service

echo ""
echo -e "${GREEN}所有服務已啟動！${NC}"
echo "=================================="
echo -e "${BLUE}服務狀態：${NC}"
echo -e "  • 認證服務: ${GREEN}http://localhost:8001${NC}"
echo -e "  • 學習服務: ${GREEN}http://localhost:8002${NC}"
echo -e "  • 題庫服務: ${GREEN}http://localhost:8003${NC}"
echo -e "  • AI 分析服務: ${GREEN}http://localhost:8004${NC}"
echo ""
echo -e "${BLUE}API 文檔：${NC}"
echo -e "  • 認證服務: ${GREEN}http://localhost:8001/docs${NC}"
echo -e "  • 學習服務: ${GREEN}http://localhost:8002/docs${NC}"
echo -e "  • 題庫服務: ${GREEN}http://localhost:8003/docs${NC}"
echo -e "  • AI 分析服務: ${GREEN}http://localhost:8004/docs${NC}"
echo ""
echo -e "${YELLOW}管理命令：${NC}"
echo -e "  • 查看所有 screen 會話: ${BLUE}screen -ls${NC}"
echo -e "  • 進入特定服務: ${BLUE}screen -r <service-name>${NC}"
echo -e "  • 停止所有服務: ${BLUE}./stop_services.sh${NC}" 