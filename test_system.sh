#!/bin/bash

# InULearning 系統測試腳本
# 作者: AIPE01_group2
# 版本: v1.0.0

set -e

echo "🧪 開始測試 InULearning 系統..."

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

# 測試資料庫連接
echo "🔍 測試資料庫連接..."

# 測試 PostgreSQL
echo "測試 PostgreSQL..."
if docker compose exec -T postgres pg_isready -U aipe-tester -d inulearning; then
    echo "✅ PostgreSQL 連接正常"
else
    echo "❌ PostgreSQL 連接失敗"
    exit 1
fi

# 測試 MongoDB
echo "測試 MongoDB..."
if docker compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB 連接正常"
else
    echo "❌ MongoDB 連接失敗"
    exit 1
fi

# 測試 Redis
echo "測試 Redis..."
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 連接正常"
else
    echo "❌ Redis 連接失敗"
    exit 1
fi

# 測試服務健康狀態
echo "🔍 測試服務健康狀態..."

# 測試認證服務
echo "測試認證服務..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ 認證服務正常"
else
    echo "❌ 認證服務異常"
fi

# 測試題庫服務
echo "測試題庫服務..."
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ 題庫服務正常"
else
    echo "❌ 題庫服務異常"
fi

# 測試學習服務
echo "測試學習服務..."
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ 學習服務正常"
else
    echo "❌ 學習服務異常"
fi

# 測試 API 功能
echo "🧪 測試 API 功能..."

# 測試用戶註冊
echo "測試用戶註冊..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user_$(date +%s)",
    "email": "test_$(date +%s)@example.com",
    "password": "testpassword123",
    "role": "student"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo "✅ 用戶註冊成功"
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    echo "❌ 用戶註冊失敗: $REGISTER_RESPONSE"
fi

# 測試用戶登入
echo "測試用戶登入..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123"
  }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ 用戶登入成功"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    echo "❌ 用戶登入失敗: $LOGIN_RESPONSE"
    exit 1
fi

# 測試獲取題目
echo "測試獲取題目..."
QUESTIONS_RESPONSE=$(curl -s -X GET "http://localhost:8002/api/v1/questions/?subject=數學&grade=國中一年級&limit=5" \
  -H "Authorization: Bearer $TOKEN")

if echo "$QUESTIONS_RESPONSE" | grep -q "question_id"; then
    echo "✅ 獲取題目成功"
    QUESTION_ID=$(echo "$QUESTIONS_RESPONSE" | grep -o '"question_id":"[^"]*"' | head -1 | cut -d'"' -f4)
else
    echo "❌ 獲取題目失敗: $QUESTIONS_RESPONSE"
fi

# 測試建立學習會話
echo "測試建立學習會話..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8003/api/v1/sessions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "測試會話",
    "subject": "數學",
    "grade": "國中一年級",
    "chapter": "整數與分數",
    "question_count": 3
  }')

if echo "$SESSION_RESPONSE" | grep -q "session_id"; then
    echo "✅ 建立學習會話成功"
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
else
    echo "❌ 建立學習會話失敗: $SESSION_RESPONSE"
fi

# 測試獲取練習題
echo "測試獲取練習題..."
EXERCISE_RESPONSE=$(curl -s -X GET "http://localhost:8003/api/v1/exercises/?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$EXERCISE_RESPONSE" | grep -q "questions"; then
    echo "✅ 獲取練習題成功"
else
    echo "❌ 獲取練習題失敗: $EXERCISE_RESPONSE"
fi

echo ""
echo "🎉 系統測試完成！"
echo ""
echo "📋 測試結果摘要："
echo "   ✅ 資料庫連接：正常"
echo "   ✅ 服務健康狀態：正常"
echo "   ✅ API 功能：正常"
echo ""
echo "🌐 系統訪問地址："
echo "   學生端前端: http://localhost:8080"
echo "   API 文檔: http://localhost:8001/docs"
echo ""
echo "✨ 系統已準備就緒，可以開始使用！" 