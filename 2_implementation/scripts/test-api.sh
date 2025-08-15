#!/bin/bash

# API 測試腳本
echo "🧪 開始測試 InULearning API 服務..."

# API 端點配置
declare -A endpoints=(
    ["認證服務"]="http://localhost:8001/health"
    ["題庫服務"]="http://localhost:8002/health"
    ["學習服務"]="http://localhost:8003/health"
    ["AI分析服務"]="http://localhost:8004/health"
    ["Nginx網關"]="http://localhost/api/health"
)

# 測試函數
test_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "測試 $name ($url)... "
    
    if response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$url" 2>/dev/null); then
        http_code="${response: -3}"
        if [ "$http_code" -eq 200 ]; then
            echo "✅ 成功 (HTTP $http_code)"
            if [ -s /tmp/response.json ]; then
                echo "   回應: $(cat /tmp/response.json | head -c 100)..."
            fi
        else
            echo "⚠️  HTTP $http_code"
        fi
    else
        echo "❌ 連接失敗"
    fi
}

# 執行測試
for service in "${!endpoints[@]}"; do
    test_endpoint "$service" "${endpoints[$service]}"
done

echo ""
echo "🔍 詳細API測試..."

# 測試具體API端點
echo "測試學習記錄API..."
curl -s -X GET "http://localhost:8003/learning/records" \
    -H "Content-Type: application/json" | head -c 200

echo ""
echo "測試題目API..."
curl -s -X GET "http://localhost:8002/questions" \
    -H "Content-Type: application/json" | head -c 200

echo ""
echo "🏁 API測試完成"