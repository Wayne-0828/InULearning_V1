# 🧪 InULearning 功能測試指南

## 📋 測試概述

本指南將幫助您測試 InULearning 平台的所有已實作功能。根據 WBS 檢查清單，您已完成以下服務：

- ✅ **auth-service** (認證服務)
- ✅ **question-bank-service** (題庫服務)
- ✅ **learning-service** (學習服務)
- ✅ **ai-analysis-service** (AI 分析服務)

## 🚀 快速測試流程

### 1. 準備測試環境

```bash
# 進入 Docker 目錄
cd InULearning_V1/4_deployment/docker

# 複製測試環境變數
cp env.test .env

# 編輯 .env 檔案，設定您的 GEMINI_API_KEY
nano .env
```

### 2. 啟動測試環境

```bash
# 方法一：使用測試腳本 (推薦)
chmod +x test_services.sh
./test_services.sh

# 方法二：手動啟動
docker compose -f docker-compose.test.yml up -d
```

### 3. 啟動後端服務

```bash
# 進入實作目錄
cd ../../2_implementation

# 啟動虛擬環境
source venv/bin/activate

# 啟動所有服務
./start_services.sh
```

## 🧪 功能測試清單

### 1. 認證服務測試 (auth-service)

**API 文檔**: http://localhost:8000/docs

#### 測試案例：

```bash
# 1. 健康檢查
curl http://localhost:8000/health

# 2. 註冊新用戶
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "email": "student@test.com",
    "password": "test123",
    "role": "student"
  }'

# 3. 用戶登入
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "test123"
  }'

# 4. 獲取用戶資料 (需要 Token)
curl -X GET "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 2. 題庫服務測試 (question-bank-service)

**API 文檔**: http://localhost:8002/docs

#### 測試案例：

```bash
# 1. 健康檢查
curl http://localhost:8002/health

# 2. 創建章節
curl -X POST "http://localhost:8002/api/v1/chapters/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "數學基礎",
    "subject": "數學",
    "grade": "國中一年級",
    "version": "108課綱"
  }'

# 3. 創建知識點
curl -X POST "http://localhost:8002/api/v1/knowledge-points/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "整數運算",
    "chapter_id": "CHAPTER_ID_HERE",
    "description": "整數的加減乘除運算"
  }'

# 4. 創建題目
curl -X POST "http://localhost:8002/api/v1/questions/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "計算 15 + (-8) = ?",
    "options": ["7", "23", "-7", "-23"],
    "correct_answer": "7",
    "explanation": "15 + (-8) = 15 - 8 = 7",
    "subject": "數學",
    "grade": "國中一年級",
    "chapter": "整數運算",
    "knowledge_point": "整數運算",
    "difficulty": "easy"
  }'

# 5. 獲取題目列表
curl -X GET "http://localhost:8002/api/v1/questions/"

# 6. 隨機獲取題目
curl -X GET "http://localhost:8002/api/v1/questions/random/?count=5"
```

### 3. 學習服務測試 (learning-service)

**API 文檔**: http://localhost:8001/docs

#### 測試案例：

```bash
# 1. 健康檢查
curl http://localhost:8001/health

# 2. 創建學習會話
curl -X POST "http://localhost:8001/api/v1/learning/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID_HERE",
    "subject": "數學",
    "grade": "國中一年級"
  }'

# 3. 創建練習
curl -X POST "http://localhost:8001/api/v1/learning/exercises/create" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_HERE",
    "subject": "數學",
    "difficulty": "medium",
    "question_count": 5
  }'

# 4. 提交答案
curl -X POST "http://localhost:8001/api/v1/learning/exercises/SESSION_ID/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "QUESTION_ID_HERE",
        "selected_answer": "7",
        "time_spent": 30
      }
    ]
  }'

# 5. 獲取學習建議
curl -X GET "http://localhost:8001/api/v1/learning/recommendations/learning?user_id=USER_ID_HERE"
```

### 4. AI 分析服務測試 (ai-analysis-service)

**API 文檔**: http://localhost:8004/docs

#### 測試案例：

```bash
# 1. 健康檢查
curl http://localhost:8004/health

# 2. 弱點分析
curl -X POST "http://localhost:8004/api/v1/learning/analysis/weakness" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_HERE",
    "answers": [
      {
        "question_id": "QUESTION_ID_HERE",
        "selected_answer": "7",
        "correct_answer": "7",
        "is_correct": true,
        "time_spent": 30
      }
    ]
  }'

# 3. 獲取學習建議
curl -X GET "http://localhost:8004/api/v1/learning/recommendations?user_id=USER_ID_HERE"
```

## 🔍 資料庫測試

### PostgreSQL 測試

```bash
# 連接到 PostgreSQL
docker exec -it inulearning_postgresql_test psql -U aipe-tester -d inulearning_test

# 查看資料表
\dt

# 查看用戶資料
SELECT * FROM users LIMIT 5;
```

### MongoDB 測試

```bash
# 連接到 MongoDB
docker exec -it inulearning_mongodb_test mongosh -u aipe-tester -p aipe-tester

# 切換到測試資料庫
use inulearning_test

# 查看集合
show collections

# 查看題目資料
db.questions.find().limit(5)
```

### Redis 測試

```bash
# 連接到 Redis
docker exec -it inulearning_redis_test redis-cli -a redis_password

# 測試連接
ping

# 查看所有鍵
keys *
```

## 📊 監控與除錯

### 查看服務日誌

```bash
# 查看所有服務日誌
docker compose -f docker-compose.test.yml logs -f

# 查看特定服務日誌
docker compose -f docker-compose.test.yml logs auth-service
```

### 檢查服務狀態

```bash
# 查看所有容器狀態
docker compose -f docker-compose.test.yml ps

# 查看資源使用情況
docker stats
```

## 🧹 清理測試環境

```bash
# 停止所有服務
docker compose -f docker-compose.test.yml down

# 清理資料卷 (會清除所有測試資料)
docker compose -f docker-compose.test.yml down -v

# 清理 Docker 映像檔 (可選)
docker system prune -a
```

## 🚨 常見問題與解決方案

### 1. 端口衝突

```bash
# 檢查端口使用情況
sudo netstat -tulpn | grep :8000

# 殺死佔用端口的進程
sudo kill -9 <PID>
```

### 2. 資料庫連接失敗

```bash
# 檢查資料庫容器狀態
docker compose -f docker-compose.test.yml ps

# 重啟資料庫服務
docker compose -f docker-compose.test.yml restart postgresql
```

### 3. AI 服務無法連接

- 確認 `GEMINI_API_KEY` 已正確設定
- 檢查網路連接
- 查看 AI 服務日誌

### 4. 記憶體不足

```bash
# 增加 Docker 記憶體限制
# 在 Docker Desktop 設定中調整
```

## 📈 測試結果記錄

建議您記錄以下資訊：

1. **測試日期**: 
2. **測試環境**: Docker 版本、作業系統
3. **測試結果**: 每個服務的測試狀態
4. **發現問題**: 記錄任何錯誤或異常
5. **效能數據**: API 回應時間、資源使用情況

## 🎯 下一步

完成基本功能測試後，建議：

1. **整合測試**: 測試服務間的相互調用
2. **效能測試**: 進行負載測試
3. **安全性測試**: 檢查認證和授權機制
4. **用戶體驗測試**: 模擬真實用戶操作流程 