# InULearning Auth Service

認證與用戶管理服務，負責處理用戶註冊、登入、JWT 認證和用戶檔案管理。

## 🚀 功能特色

- **多角色支援**: 支援學生、家長、教師三種角色
- **JWT 認證**: 使用 JWT 進行安全的身份驗證
- **Token 刷新**: 支援 Access Token 和 Refresh Token 機制
- **用戶管理**: 完整的用戶檔案 CRUD 操作
- **安全密碼**: 使用 bcrypt 進行密碼雜湊
- **資料庫遷移**: 使用 Alembic 管理資料庫結構變更

## 📋 API 端點

### 認證相關

| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用戶註冊 |
| POST | `/api/v1/auth/login` | 用戶登入 |
| POST | `/api/v1/auth/refresh` | 刷新 Access Token |
| POST | `/api/v1/auth/logout` | 登出 (撤銷 Refresh Token) |
| POST | `/api/v1/auth/logout-all` | 登出所有裝置 |

### 用戶管理

| 方法 | 端點 | 描述 |
|------|------|------|
| GET | `/api/v1/users/profile` | 獲取當前用戶檔案 |
| PATCH | `/api/v1/users/profile` | 更新當前用戶檔案 |
| GET | `/api/v1/users/{user_id}` | 獲取指定用戶檔案 |

## 🛠️ 技術棧

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Migrations**: Alembic
- **Testing**: pytest

## 📦 安裝與設置

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境變數設置

複製 `.env.example` 並設置必要的環境變數：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/inulearning_auth

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 3. 資料庫遷移

```bash
# 初始化 Alembic
alembic init alembic

# 執行遷移
alembic upgrade head
```

### 4. 啟動服務

```bash
# 開發模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生產模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 測試

### 執行測試

```bash
# 執行所有測試
pytest

# 執行測試並顯示覆蓋率
pytest --cov=app

# 執行特定測試檔案
pytest tests/test_auth.py
```

### 測試覆蓋率

```bash
pytest --cov=app --cov-report=html
```

## 📚 API 文檔

啟動服務後，可以透過以下端點查看 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 開發指南

### 專案結構

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式
│   ├── config.py            # 配置設定
│   ├── database.py          # 資料庫連接
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 模型
│   ├── auth.py              # JWT 認證功能
│   ├── crud.py              # 資料庫操作
│   ├── dependencies.py      # FastAPI 依賴
│   └── api/
│       ├── __init__.py
│       ├── auth.py          # 認證路由
│       └── users.py         # 用戶管理路由
├── alembic/                 # 資料庫遷移
├── tests/                   # 測試檔案
├── requirements.txt         # Python 依賴
├── Dockerfile              # Docker 配置
└── README.md               # 專案文檔
```

### 新增 API 端點

1. 在 `app/api/` 目錄下建立新的路由檔案
2. 在 `app/main.py` 中註冊路由
3. 撰寫對應的測試

### 資料庫變更

1. 修改 `app/models.py` 中的模型
2. 生成遷移檔案：`alembic revision --autogenerate -m "描述"`
3. 執行遷移：`alembic upgrade head`

## 🐳 Docker 部署

### 建立映像檔

```bash
docker build -t inulearning-auth-service .
```

### 執行容器

```bash
docker run -p 8000:8000 inulearning-auth-service
```

## 🔒 安全考量

- 使用 bcrypt 進行密碼雜湊
- JWT Token 有過期時間
- Refresh Token 可被撤銷
- 支援 CORS 設定
- 輸入驗證使用 Pydantic

## 📝 日誌

服務會記錄以下資訊：
- API 請求/回應
- 認證事件
- 錯誤和異常
- 資料庫操作

## 🤝 貢獻

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發起 Pull Request

## 📄 授權

本專案採用 MIT 授權條款。 