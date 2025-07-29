# InULearning Docker 部署指南

## 🚀 快速開始

### 前置需求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB RAM
- 至少 10GB 可用磁碟空間

### 一鍵啟動

```bash
# 克隆專案（如果還沒有的話）
git clone <repository-url>
cd InULearning_V1

# 給予執行權限
chmod +x start.sh stop.sh

# 啟動系統
./start.sh
```

### 手動啟動

```bash
# 建立環境變數檔案
cp env.example .env

# 建立必要目錄
mkdir -p logs init-scripts nginx/conf.d

# 啟動服務
docker-compose up --build -d
```

## 📋 系統架構

### 服務組成

| 服務 | 端口 | 描述 |
|------|------|------|
| **學生端前端** | 8080 | 學生學習介面 |
| **認證服務** | 8001 | 用戶認證與管理 |
| **題庫服務** | 8002 | 題目管理與查詢 |
| **學習服務** | 8003 | 學習流程與記錄 |
| **PostgreSQL** | 5432 | 用戶資料與學習記錄 |
| **MongoDB** | 27017 | 題庫資料 |
| **Redis** | 6379 | 快取與會話 |
| **MinIO** | 9000/9001 | 檔案儲存 |

### 資料庫設計

#### PostgreSQL 表結構
- `users`: 用戶資訊
- `learning_sessions`: 學習會話
- `exercise_records`: 練習記錄
- `learning_progress`: 學習進度

#### MongoDB 集合
- `questions`: 題目資料
- `chapters`: 章節資訊
- `knowledge_points`: 知識點

## 🔧 配置說明

### 環境變數

主要配置檔案：`.env`

```bash
# 資料庫配置
POSTGRES_DB=inulearning
POSTGRES_USER=inulearning_user
POSTGRES_PASSWORD=inulearning_password

# MongoDB 配置
MONGO_INITDB_ROOT_USERNAME=inulearning_admin
MONGO_INITDB_ROOT_PASSWORD=inulearning_password

# MinIO 配置
MINIO_ROOT_USER=inulearning_admin
MINIO_ROOT_PASSWORD=inulearning_password

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 網路配置

- 內部網路：`inulearning_network`
- 外部訪問：通過 Nginx 反向代理

## 📊 監控與日誌

### 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f auth-service
docker-compose logs -f learning-service
docker-compose logs -f question-bank-service

# 查看資料庫日誌
docker-compose logs -f postgres
docker-compose logs -f mongodb
```

### 健康檢查

```bash
# 檢查服務狀態
docker-compose ps

# 檢查健康狀態
curl http://localhost:8001/health  # 認證服務
curl http://localhost:8002/health  # 題庫服務
curl http://localhost:8003/health  # 學習服務
```

## 🧪 測試功能

### 測試帳號

系統預設提供以下測試帳號：

| 角色 | 用戶名 | 密碼 | 說明 |
|------|--------|------|------|
| 學生 | test_student | password123 | 用於測試學生功能 |
| 教師 | test_teacher | password123 | 用於測試教師功能 |

### API 測試

```bash
# 登入測試
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_student", "password": "password123"}'

# 獲取題目
curl -X GET http://localhost:8002/api/v1/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 建立學習會話
curl -X POST http://localhost:8003/api/v1/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subject": "數學", "grade": "國中一年級", "chapter": "整數與分數", "question_count": 5}'
```

## 🔄 開發模式

### 本地開發

```bash
# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

# 查看開發日誌
docker-compose -f docker-compose.dev.yml logs -f
```

### 程式碼修改

1. 修改程式碼
2. 重新建置容器：`docker-compose build [service-name]`
3. 重啟服務：`docker-compose restart [service-name]`

## 🚨 故障排除

### 常見問題

#### 1. 服務無法啟動

```bash
# 檢查容器狀態
docker-compose ps

# 查看詳細錯誤
docker-compose logs [service-name]

# 重新建置
docker-compose down
docker-compose up --build -d
```

#### 2. 資料庫連接失敗

```bash
# 檢查資料庫狀態
docker-compose exec postgres pg_isready -U inulearning_user -d inulearning
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# 重新初始化資料庫
docker-compose down -v
docker-compose up -d
```

#### 3. 端口衝突

```bash
# 檢查端口使用情況
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :8003

# 修改 docker-compose.yml 中的端口映射
```

### 清理環境

```bash
# 停止並移除所有容器
docker-compose down

# 移除所有資料（包括資料庫資料）
docker-compose down -v

# 清理未使用的資源
docker system prune -f
```

## 📈 效能優化

### 資源配置

```yaml
# 在 docker-compose.yml 中為服務添加資源限制
services:
  auth-service:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### 快取配置

- Redis 用於會話快取
- 資料庫查詢結果快取
- 靜態資源快取

## 🔒 安全考量

### 生產環境配置

1. 修改預設密碼
2. 啟用 HTTPS
3. 配置防火牆
4. 定期備份資料
5. 監控系統日誌

### 資料備份

```bash
# PostgreSQL 備份
docker-compose exec postgres pg_dump -U inulearning_user inulearning > backup.sql

# MongoDB 備份
docker-compose exec mongodb mongodump --db inulearning --out /backup
```

## 📞 支援

如有問題，請：

1. 查看日誌：`docker-compose logs -f`
2. 檢查健康狀態：`docker-compose ps`
3. 重新啟動服務：`docker-compose restart`
4. 提交 Issue 到專案倉庫

---

**版本**: v1.0.0  
**最後更新**: 2024-12-19  
**維護者**: AIPE01_group2 