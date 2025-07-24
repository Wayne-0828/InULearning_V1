# InULearning Learning Service

InULearning 個人化學習平台的核心學習服務，負責個人化練習會話管理、答案批改、學習歷程追蹤等功能。

## 🚀 功能特色

### 核心功能
- **個人化練習會話管理** - 根據用戶學習檔案創建個人化練習
- **答案提交與自動批改** - 處理學生答案並提供即時反饋
- **學習歷程追蹤** - 記錄詳細的學習數據和進度
- **AI 弱點分析整合** - 與 AI 分析服務整合，提供深度分析
- **學習趨勢分析** - 提供學習進步趨勢和預測

### API 端點
- **練習管理** (`/api/v1/exercises/`) - 創建、提交、查詢練習會話
- **會話管理** (`/api/v1/sessions/`) - 會話列表、詳情、統計
- **學習推薦** (`/api/v1/recommendations/`) - 個人化建議、弱點分析
- **趨勢分析** (`/api/v1/trends/`) - 學習趨勢、表現預測

## 🛠️ 技術架構

### 後端技術棧
- **FastAPI** - 現代化 Python Web 框架
- **SQLAlchemy** - ORM 和資料庫操作
- **PostgreSQL** - 主要資料庫
- **Pydantic** - 資料驗證和序列化
- **httpx** - 異步 HTTP 客戶端

### 服務架構
- **微服務架構** - 與題庫服務、AI 分析服務解耦
- **異步處理** - 支援高併發請求
- **RESTful API** - 標準化的 API 設計
- **JWT 認證** - 安全的用戶認證機制

## 📦 安裝與部署

### 環境需求
- Python 3.8+
- PostgreSQL 12+
- Redis (可選，用於快取)

### 快速開始

1. **克隆專案**
```bash
git clone <repository-url>
cd learning-service
```

2. **建立虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **配置環境變數**
```bash
cp env.example .env
# 編輯 .env 文件，設定資料庫連接等配置
```

5. **初始化資料庫**
```bash
# 確保 PostgreSQL 服務運行中
# 創建資料庫
createdb inulearning

# 運行資料庫遷移（如果使用 Alembic）
alembic upgrade head
```

6. **啟動服務**
```bash
python run.py
```

服務將在 `http://localhost:8002` 啟動

### Docker 部署

```bash
# 構建映像
docker build -t inulearning-learning-service .

# 運行容器
docker run -p 8002:8002 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  inulearning-learning-service
```

## 📚 API 文檔

啟動服務後，可透過以下方式查看 API 文檔：

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI JSON**: http://localhost:8002/openapi.json

### 主要 API 端點

#### 練習管理
```http
POST /api/v1/exercises/create
POST /api/v1/exercises/{session_id}/submit
GET  /api/v1/exercises/{session_id}/status
DELETE /api/v1/exercises/{session_id}
```

#### 會話管理
```http
GET /api/v1/sessions/
GET /api/v1/sessions/{session_id}
GET /api/v1/sessions/statistics/summary
```

#### 學習推薦
```http
GET /api/v1/recommendations/learning
GET /api/v1/recommendations/weaknesses
GET /api/v1/recommendations/practice-suggestions
```

#### 趨勢分析
```http
GET /api/v1/trends/learning
GET /api/v1/trends/performance-prediction
GET /api/v1/trends/progress-chart
GET /api/v1/trends/subject-comparison
GET /api/v1/trends/weekly-report
```

## 🧪 測試

### 運行測試
```bash
# 運行所有測試
pytest

# 運行特定測試文件
pytest tests/test_main.py

# 生成覆蓋率報告
pytest --cov=src tests/
```

### 測試配置
- 使用 `pytest` 作為測試框架
- 支援異步測試
- 包含單元測試和整合測試
- 使用測試資料庫避免影響生產數據

## 🔧 開發指南

### 專案結構
```
learning-service/
├── src/
│   ├── main.py              # 應用程式入口點
│   ├── models/              # 資料模型
│   │   ├── base.py
│   │   ├── learning_session.py
│   │   └── schemas.py
│   ├── routers/             # API 路由
│   │   ├── exercises.py
│   │   ├── sessions.py
│   │   ├── recommendations.py
│   │   └── trends.py
│   ├── services/            # 業務邏輯
│   │   ├── exercise_service.py
│   │   ├── question_bank_client.py
│   │   └── ai_analysis_client.py
│   └── utils/               # 工具函數
│       ├── database.py
│       ├── auth.py
│       └── logging_config.py
├── tests/                   # 測試文件
├── requirements.txt         # Python 依賴
├── env.example             # 環境變數範例
├── run.py                  # 啟動腳本
└── README.md               # 專案說明
```

### 開發流程
1. 建立功能分支
2. 實作功能並編寫測試
3. 運行測試確保通過
4. 提交程式碼並發起 Pull Request
5. 程式碼審查和合併

### 程式碼風格
- 使用 `black` 進行程式碼格式化
- 使用 `isort` 排序 import 語句
- 使用 `flake8` 進行程式碼檢查
- 遵循 PEP 8 程式碼風格指南

## 🔒 安全性

### 認證與授權
- 使用 JWT Token 進行用戶認證
- 支援角色基礎的權限控制
- API 端點需要有效的認證 Token

### 資料安全
- 所有敏感資料都經過加密
- 使用 HTTPS 進行資料傳輸
- 實作資料庫連接池和查詢優化

## 📊 監控與日誌

### 日誌配置
- 使用結構化日誌記錄
- 支援不同日誌級別
- 可配置日誌輸出格式

### 健康檢查
```http
GET /health
```

回應範例：
```json
{
  "status": "healthy",
  "service": "inulearning-learning-service",
  "version": "v1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 📞 聯絡資訊

- 專案維護者: AIPE01_group2
- 專案連結: [GitHub Repository]
- 問題回報: [GitHub Issues]

## 🔄 更新日誌

### v1.0.0 (2024-01-01)
- 初始版本發布
- 實作核心學習服務功能
- 支援個人化練習會話管理
- 整合 AI 分析服務
- 提供完整的 RESTful API 