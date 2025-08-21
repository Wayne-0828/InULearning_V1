# 題庫資料載入指南

## 概述

本指南說明如何將 `seeds/全題庫` 目錄中的題目資料載入到 MongoDB 和 MinIO 中。

## 功能特色

- ✅ 自動載入所有科目的題目資料
- ✅ 支援圖片上傳到 MinIO
- ✅ 標準化題目格式
- ✅ 自動生成唯一 ID
- ✅ 支援批量處理
- ✅ 完整的錯誤處理和日誌

## 資料結構

### MongoDB Schema

```json
{
  "_id": "uuid4-generated-id",
  "question_id": "uuid4-generated-id", 
  "subject": "科目名稱",
  "grade": "年級代碼 (7A, 7B, 8A, 8B, 9A, 9B)",
  "publisher": "出版社 (南一, 康軒, 翰林)",
  "chapter": "章節名稱",
  "topic": "主題",
  "knowledge_points": ["知識點1", "知識點2"],
  "question_type": "選擇題",
  "difficulty": "easy|medium|hard",
  "content": "題目內容",
  "options": [
    {"key": "A", "text": "選項A"},
    {"key": "B", "text": "選項B"},
    {"key": "C", "text": "選項C"},
    {"key": "D", "text": "選項D"}
  ],
  "correct_answer": "正確答案 (A, B, C, D)",
  "explanation": "解析說明",
  "image_filename": "圖片檔名 (如果有)",
  "image_url": "圖片API路徑 (如果有)",
  "source_file": "來源檔案名稱",
  "created_at": "創建時間",
  "updated_at": "更新時間"
}
```

### MinIO 儲存結構

```
question-bank/
├── images/
│   ├── abc123...xyz.jpg
│   ├── def456...uvw.jpg
│   └── ...
```

## 執行步驟

### 方法一：Docker 執行 (推薦)

#### 1. 使用 Docker Compose 啟動服務

```bash
cd 2_implementation/backend/question-bank-service

# 啟動 MongoDB 和 MinIO
docker compose -f docker-compose.data-loading.yml up -d mongodb minio

# 等待服務啟動 (約30秒)
sleep 30

# 執行資料載入
docker compose -f docker-compose.data-loading.yml up data-loader

# 清理容器 (可選)
docker compose -f docker-compose.data-loading.yml down
```

#### 2. 檢查結果

訪問 MinIO Web 界面：http://localhost:9001
- 用戶名：inulearning_admin
- 密碼：inulearning_password

### 方法二：本地執行

#### 1. 環境準備

確保以下服務正在運行：
- MongoDB (預設: mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning)
- MinIO (預設: localhost:9000)

#### 2. 安裝依賴

```bash
cd 2_implementation/backend/question-bank-service
pip install -r requirements.txt
```

#### 3. 測試連接

```bash
python test_data_loading.py
```

#### 4. 執行完整資料載入

```bash
python load_rawdata.py
```

或使用執行腳本：

```bash
./run_data_loading.sh
```

## 預期結果

執行成功後，您應該看到：

```
🚀 開始載入題庫資料...
✅ MongoDB 連接成功
✅ MinIO bucket 已存在: question-bank
✅ 已清空 MongoDB 題目資料: 0 筆
✅ 已清空 MinIO 圖片資料
🖼️ 開始上傳圖片...
📁 處理圖片目錄: .../全題庫/自然/images
📊 已上傳 50 張圖片...
📊 已上傳 100 張圖片...
✅ 圖片上傳完成，共 XXX 張
📚 開始載入題目資料...
📖 載入檔案: 國文/南一_國文.json
📊 已載入 100 道題目...
📊 已載入 200 道題目...
✅ 題目載入完成，共 XXXXX 道
🎉 資料載入完成！共載入 XXXXX 道題目，XXX 張圖片
✅ 資料載入完成！
```

## 支援的資料格式

### JSON 題目格式

```json
{
  "grade": "7A",
  "subject": "國文", 
  "publisher": "南一",
  "chapter": "夏夜",
  "topic": "新詩",
  "knowledge_point": ["轉化", "擬人法"],
  "difficulty": "easy",
  "question": "題目內容...",
  "options": {
    "A": "選項A",
    "B": "選項B", 
    "C": "選項C",
    "D": "選項D"
  },
  "answer": "C",
  "explanation": "解析說明..."
}
```

### 圖片格式

- 支援 `.jpg` 格式
- SHA256 檔名格式 (64字元十六進位)
- 自動上傳到 MinIO 的 `images/` 目錄

## 錯誤處理

腳本包含完整的錯誤處理：

- ❌ 連接失敗：自動重試並報告錯誤
- ⚠️ 資料格式錯誤：跳過並記錄警告
- 📊 進度報告：每處理100道題目或50張圖片報告一次進度

## 驗證資料載入

### 檢查 MongoDB

```bash
# 連接到 MongoDB
mongo mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning

# 檢查題目數量
db.questions.count()

# 查看範例題目
db.questions.findOne()

# 按科目統計
db.questions.aggregate([
  {$group: {_id: "$subject", count: {$sum: 1}}}
])
```

### 檢查 MinIO

訪問 MinIO Web 介面：http://localhost:9000
- 用戶名：aipe-tester
- 密碼：aipe-tester

檢查 `question-bank/images/` 目錄中的圖片。

## 故障排除

### 常見問題

1. **MongoDB 連接失敗**
   - 檢查 MongoDB 服務是否運行
   - 確認連接字串正確
   - 檢查網路連接

2. **MinIO 上傳失敗**
   - 檢查 MinIO 服務是否運行
   - 確認存取金鑰正確
   - 檢查磁碟空間

3. **記憶體不足**
   - 大量資料載入可能需要較多記憶體
   - 考慮分批處理或增加記憶體

### 日誌檢查

腳本會輸出詳細的日誌資訊，包括：
- 連接狀態
- 處理進度
- 錯誤詳情
- 統計資訊

## 注意事項

⚠️ **重要警告**：
- 腳本會清空現有的題目資料和圖片
- 生產環境使用前請先備份
- 大量資料載入可能需要較長時間

📝 **建議**：
- 首次使用建議先執行測試腳本
- 定期備份資料庫
- 監控磁碟空間使用情況