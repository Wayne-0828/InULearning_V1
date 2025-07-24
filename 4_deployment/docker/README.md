# 🐳 InULearning Docker 開發環境設定

## 📋 概述

本目錄包含 InULearning 智慧學習平台的 Docker 開發環境設定檔案。

## 📁 檔案說明

### `docker-compose.dev.yml`
- 完整的開發環境 Docker Compose 設定
- 包含所有必要的服務：資料庫、微服務、前端應用、監控工具
- 使用環境變數來管理敏感資訊

### `env.example`
- 環境變數範例檔案
- 包含所有必要的密碼和設定值範例
- **請複製為 `.env` 並填入您的實際密碼**

## 🚀 快速開始

### 1. 設定環境變數

```bash
# 複製環境變數範例檔案
cp env.example .env

# 編輯 .env 檔案，填入您的密碼和 API 金鑰
nano .env
```

### 2. 啟動開發環境

```bash
# 啟動所有服務
docker compose -f docker-compose.dev.yml up -d

# 查看服務狀態
docker compose -f docker-compose.dev.yml ps

# 查看服務日誌
docker compose -f docker-compose.dev.yml logs -f
```

### 3. 停止開發環境

```bash
# 停止所有服務
docker compose -f docker-compose.dev.yml down

# 停止服務並移除資料卷（會清除所有資料）
docker compose -f docker-compose.dev.yml down -v
```

## 🌐 服務端口對應

| 服務 | 端口 | 說明 |
|------|------|------|
| Nginx (API Gateway) | 8000 | 主要 API 入口 |
| Auth Service | 8001 | 認證服務 |
| Learning Service | 8002 | 學習服務 |
| Question Bank Service | 8003 | 題庫服務 |
| AI Analysis Service | 8004 | AI 分析服務 |
| Student App | 3000 | 學生端前端 |
| Parent App | 3001 | 家長端前端 |
| Teacher App | 3002 | 教師端前端 |
| Grafana | 3003 | 監控儀表板 |
| PostgreSQL | 5432 | 關聯式資料庫 |
| MongoDB | 27017 | 文件資料庫 |
| Redis | 6379 | 快取資料庫 |
| Milvus | 19530 | 向量資料庫 |
| MinIO | 9000 | 對象儲存 |
| MinIO Console | 9001 | MinIO 管理介面 |
| RabbitMQ | 5672 | 訊息佇列 |
| RabbitMQ Management | 15672 | RabbitMQ 管理介面 |
| Prometheus | 9090 | 監控系統 |

## 🔐 安全注意事項

1. **永遠不要將 `.env` 檔案提交到版本控制系統**
2. **定期更換密碼**
3. **使用強密碼**
4. **限制網路存取**

## 🛠️ 常用指令

```bash
# 重建特定服務
docker compose -f docker-compose.dev.yml build auth-service

# 重啟特定服務
docker compose -f docker-compose.dev.yml restart auth-service

# 查看特定服務日誌
docker compose -f docker-compose.dev.yml logs auth-service

# 進入容器內部
docker compose -f docker-compose.dev.yml exec postgresql psql -U aipe-tester -d inulearning

# 備份資料庫
docker compose -f docker-compose.dev.yml exec postgresql pg_dump -U aipe-tester inulearning > backup.sql
```

## 🔧 故障排除

### 常見問題

1. **端口衝突**
   ```bash
   # 檢查端口使用情況
   netstat -tulpn | grep :8000
   ```

2. **權限問題**
   ```bash
   # 確保 Docker 有足夠權限
   sudo usermod -aG docker $USER
   ```

3. **記憶體不足**
   ```bash
   # 增加 Docker 記憶體限制
   # 在 Docker Desktop 設定中調整
   ```

## 📝 開發建議

1. **使用 `.env` 檔案管理所有密碼**
2. **定期備份重要資料**
3. **監控服務健康狀態**
4. **使用 Docker 網路隔離服務**

## 🤝 貢獻指南

1. 修改 `docker-compose.dev.yml` 時，請同時更新 `env.example`
2. 新增服務時，請更新此 README 檔案
3. 確保所有變更都經過測試 