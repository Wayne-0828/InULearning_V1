#!/bin/bash

# =============================================================================
# InULearning 服務停止腳本
# =============================================================================

# 設定顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}InULearning 服務停止腳本${NC}"
echo "=================================="

# 停止所有 screen 會話
echo -e "${BLUE}正在停止所有服務...${NC}"

# 停止認證服務
if screen -list | grep -q "auth-service"; then
    screen -S auth-service -X quit
    echo -e "${GREEN}✓ 認證服務已停止${NC}"
else
    echo -e "${YELLOW}認證服務未運行${NC}"
fi

# 停止學習服務
if screen -list | grep -q "learning-service"; then
    screen -S learning-service -X quit
    echo -e "${GREEN}✓ 學習服務已停止${NC}"
else
    echo -e "${YELLOW}學習服務未運行${NC}"
fi

# 停止題庫服務
if screen -list | grep -q "question-bank-service"; then
    screen -S question-bank-service -X quit
    echo -e "${GREEN}✓ 題庫服務已停止${NC}"
else
    echo -e "${YELLOW}題庫服務未運行${NC}"
fi

echo ""
echo -e "${GREEN}所有服務已停止！${NC}"
echo "=================================="
echo -e "${BLUE}剩餘 screen 會話：${NC}"
screen -ls 