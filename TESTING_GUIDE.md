# 📋 InULearning 功能測試指南

## 🔧 測試環境準備

### 1. 檢查服務狀態
```bash
# 檢查所有服務是否正常運行
docker compose ps

# 應該看到以下服務都是 Up 狀態：
# - inulearning_auth_service (健康)
# - inulearning_learning_service (健康)  
# - inulearning_question_bank_service (可能不健康，但能正常工作)
# - inulearning_postgres (健康)
# - inulearning_mongodb (健康)
# - inulearning_redis (健康)
# - inulearning_minio (健康)
```

### 2. 啟動缺失的服務（如果需要）
```bash
# 如果任何服務沒有運行，使用以下命令啟動
docker compose up -d

# 檢查特定服務日誌
docker logs inulearning_auth_service --tail 10
docker logs inulearning_learning_service --tail 10
docker logs inulearning_question_bank_service --tail 10
```

---

## 🥇 第一優先級功能測試：核心學習流程

### 測試 1: 學習系統與題庫整合

#### 1.1 題庫服務基本功能
```bash
# 測試題庫健康檢查
curl "http://localhost:8002/health"

# 測試搜索API
curl "http://localhost:8002/api/v1/questions/search?subject=數學&limit=3" | python3 -m json.tool

# 測試隨機出題API
curl "http://localhost:8002/api/v1/questions/random?count=2" | python3 -m json.tool
```

**預期結果**:
- 健康檢查返回 `{"status": "healthy"}`
- 搜索API返回包含 `items`, `total`, `page` 等字段的分頁數據
- 隨機API返回題目數組，每個題目包含 `id`, `question`, `options`, `answer` 等字段

#### 1.2 學習服務健康檢查
```bash
# 測試學習服務健康檢查
curl "http://localhost:8003/health"
```

**預期結果**: 返回健康狀態信息

### 測試 2: 自動批改引擎

#### 2.1 運行完整學習流程測試
```bash
# 運行端到端學習流程測試
python3 test_learning_flow.py
```

**預期結果**:
```
🚀 開始完整學習流程測試
============================================================
🔐 跳過用戶登入，專注測試核心學習功能...

📚 測試題目獲取...
✅ 成功獲取 X 道題目
📋 題目示例:
   1. [題目內容]...
      選項: ['A', 'B', 'C', 'D']
      正確答案: [答案]

🤖 測試自動批改功能...
   題目 1: 學生答案 X | 正確答案 X | ✅ 正確/❌ 錯誤 | 得分: X
   題目 2: 學生答案 X | 正確答案 X | ✅ 正確/❌ 錯誤 | 得分: X

📊 批改結果統計:
   總分: X/Y
   正確率: X% (X/Y)

💾 測試記錄儲存功能...
✅ 學習會話記錄:
   會話ID: [UUID]
   總分: X
   用時: X 秒
✅ 詳細答題記錄:
   記錄 1: [記錄詳情]
✅ 成功模擬儲存 X 條學習記錄

============================================================
🎉 完整學習流程測試完成！
```

### 測試 3: 學習系統整合測試

#### 3.1 運行學習系統整合測試
```bash
# 運行學習系統與題庫整合測試
python3 test_learning_integration.py
```

**預期結果**:
```
🚀 開始學習服務與題庫服務整合測試
==================================================
🔍 測試學習服務與題庫服務整合...

1. 測試題庫服務直接調用:
✅ 搜索API正常: 找到 X 道題目
   返回字段: ['items', 'total', 'page', 'page_size', 'total_pages']
✅ 隨機出題API正常: 返回 X 道題目
   題目字段: [字段列表]

2. 測試學習服務的題庫客戶端:
⚠️  學習服務API需要認證，跳過直接測試
   但題庫客戶端的配置已更新:
   - 服務地址: http://localhost:8002 ✅
   - 搜索API返回字段: items ✅
   - 隨機API返回格式: 直接數組 ✅

3. 測試數據轉換兼容性:
✅ 題目數據格式檢查:
   ✅ id: <class 'str'>
   ✅ question: <class 'str'>
   ✅ options: <class 'dict'>
   ✅ answer: <class 'str'>
   ✅ difficulty: <class 'str'>
✅ 所有必需字段都存在
✅ 選項格式正確 (字典): ['A', 'B', 'C', 'D']

==================================================
✅ 整合測試完成
```

---

## 🥈 第二優先級功能測試：權限與儀表板功能

### 測試 4: 關係管理功能

#### 4.1 運行關係管理測試
```bash
# 運行完整的關係管理功能測試
python3 test_relationships.py
```

**預期結果**:
```
🚀 開始關係管理功能測試
============================================================
🔐 parent用戶登入...
✅ parent登入成功
🔐 teacher用戶登入...
✅ teacher登入成功
🔐 admin用戶登入...
✅ admin登入成功

👨‍👩‍👧‍👦 測試家長-學生關係管理...
✅ 家長已有 X 個子女關係:
   - 子女: 學生 01號 (ID: 3)
   - 子女: 學生 02號 (ID: 4)

👨‍🏫 測試教師-班級關係管理...
✅ 教師已有 X 個教學關係:
   - 班級: 7A班 | 科目: 數學
   - 班級: 7B班 | 科目: 數學
✅ 系統中有 X 個班級:
   - 7A班 (7A) - 2024-2025
   - 7B班 (7B) - 2024-2025
   - 8A班 (8A) - 2024-2025
   - 8B班 (8B) - 2024-2025

👑 測試管理員班級管理...
✅ 成功創建班級: 9A班

🔒 測試權限控制...
🔐 student用戶登入...
✅ student登入成功
✅ 權限控制正常：學生無法訪問家長功能

📊 測試學習記錄查詢API...
⚠️  學習記錄API將在學習服務中實現
   - 家長查詢子女學習記錄
   - 教師查詢班級學生記錄
   - 統計數據：正確率、學習時長、進度等

============================================================
🎉 關係管理功能測試完成！

📈 測試結果總結:
   ✅ 家長-學生關係管理: 可查詢現有關係
   ✅ 教師-班級關係管理: 可查詢教學關係和班級列表
   ✅ 管理員班級管理: 可創建和管理班級
   ✅ 權限控制: 正確限制不同角色的訪問權限
   ⚠️  學習記錄API: 待實現（下一階段）
```

### 測試 5: 學習記錄查詢API

#### 5.1 手動測試學習記錄API

首先獲取認證token：
```bash
# 家長登入獲取token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "parent01@test.com", "password": "password123"}'

# 將返回的 access_token 保存，用於後續請求
```

然後測試學習記錄查詢：
```bash
# 替換 YOUR_TOKEN 為實際的 access_token
export PARENT_TOKEN="YOUR_TOKEN"

# 測試家長查詢子女學習記錄
curl -H "Authorization: Bearer $PARENT_TOKEN" \
  "http://localhost:8003/api/v1/learning/records/parent/children?limit=5"

# 測試家長查詢子女學習統計
curl -H "Authorization: Bearer $PARENT_TOKEN" \
  "http://localhost:8003/api/v1/learning/records/parent/statistics?days=30"
```

**預期結果**:
- 學習記錄查詢返回學習會話數組（可能為空，因為沒有實際學習數據）
- 統計查詢返回統計信息結構

#### 5.2 教師API測試
```bash
# 教師登入獲取token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "teacher01@test.com", "password": "password123"}'

export TEACHER_TOKEN="YOUR_TEACHER_TOKEN"

# 測試教師查詢學生學習記錄
curl -H "Authorization: Bearer $TEACHER_TOKEN" \
  "http://localhost:8003/api/v1/learning/records/teacher/students?subject=數學&limit=5"
```

---

## 🔍 手動API測試步驟

### 測試用戶信息
系統中預設的測試用戶：
- **學生**: `student01@test.com` / `password123`
- **家長**: `parent01@test.com` / `password123` 
- **教師**: `teacher01@test.com` / `password123`
- **管理員**: `admin01@test.com` / `password123`

### API端點測試

#### 認證服務 (端口 8001)
```bash
# 健康檢查
curl "http://localhost:8001/health"

# 用戶登入
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "parent01@test.com", "password": "password123"}'

# 查詢親子關係（需要token）
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8001/api/v1/relationships/parent-child"

# 查詢班級列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8001/api/v1/relationships/classes"
```

#### 題庫服務 (端口 8002)
```bash
# 健康檢查
curl "http://localhost:8002/health"

# 搜索題目
curl "http://localhost:8002/api/v1/questions/search?subject=數學&limit=3"

# 隨機題目
curl "http://localhost:8002/api/v1/questions/random?count=2"

# 題目列表
curl "http://localhost:8002/api/v1/questions/?limit=3"
```

#### 學習服務 (端口 8003)
```bash
# 健康檢查
curl "http://localhost:8003/health"

# 查詢學習記錄（需要家長token）
curl -H "Authorization: Bearer YOUR_PARENT_TOKEN" \
  "http://localhost:8003/api/v1/learning/records/parent/children"

# 查詢學習統計
curl -H "Authorization: Bearer YOUR_PARENT_TOKEN" \
  "http://localhost:8003/api/v1/learning/records/parent/statistics"
```

---

## 🚨 常見問題排除

### 問題 1: 服務無法連接
```bash
# 檢查服務狀態
docker compose ps

# 重啟特定服務
docker compose restart [service-name]

# 查看服務日誌
docker logs [container-name] --tail 20
```

### 問題 2: 數據庫連接問題
```bash
# 檢查PostgreSQL
docker exec -it inulearning_postgres psql -U aipe-tester -d inulearning -c "\dt"

# 檢查MongoDB
docker exec -it inulearning_mongodb mongosh --eval "db.adminCommand('listCollections')"
```

### 問題 3: 認證token問題
- 確保使用正確的email格式登入
- token有30分鐘有效期，過期需要重新登入
- 檢查Authorization header格式：`Bearer YOUR_TOKEN`

---

## ✅ 測試完成檢查清單

### 第一優先級功能
- [ ] 題庫服務健康檢查通過
- [ ] 題目搜索和隨機出題正常
- [ ] 學習流程測試腳本執行成功
- [ ] 自動批改邏輯正確
- [ ] 數據轉換格式正確

### 第二優先級功能  
- [ ] 所有測試用戶能正常登入
- [ ] 家長能查詢子女關係
- [ ] 教師能查詢班級關係
- [ ] 管理員能創建班級
- [ ] 權限控制正常工作
- [ ] 學習記錄API響應正確

### 系統整體
- [ ] 所有服務健康狀態正常
- [ ] 跨服務API調用正常
- [ ] 數據庫數據完整
- [ ] 錯誤處理適當

---

**請按照以上步驟進行測試，如果遇到任何問題或測試結果與預期不符，請告訴我具體的錯誤信息。測試完成後，我將開始第三優先級的開發工作。** 