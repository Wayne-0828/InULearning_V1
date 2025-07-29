# InULearning 個人化學習平台 v3.0

---

## 🎯 專案概述

InULearning 是一個基於 AI 的個人化學習平台，透過智能分析學生學習狀況，提供個人化的學習建議和治療方案。

### ✨ 核心特色
- 🤖 **AI 驅動學習分析**: 自動分析學習弱點並提供個人化建議
- 👨‍👩‍👧‍👦 **多角色支援**: 學生、家長、教師、管理員完整生態系
- 📚 **智能題庫系統**: 支援條件搜索、隨機出題、自動批改
- 📊 **學習歷程追蹤**: 完整記錄學習過程與進度分析
- 🔄 **即時回饋機制**: 即時批改、詳解顯示、錯誤分析

---

## 🚀 快速開始

### 前置需求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB RAM
- 至少 1GB 可用磁碟空間

### 一鍵啟動
```bash
# 1. 進入專案目錄
cd InULearning_V1

# 2. 啟動系統 (首次啟動需要 3-5 分鐘建置容器)
./start.sh

# 3. 驗證系統狀態
docker compose ps
```

### 訪問地址
| 服務 | 地址 | 說明 |
|------|------|------|
| 🎓 學生端 | http://localhost:8080 | 主要學習介面 |
| 👨‍👩‍👧‍👦 家長端 | http://localhost:8082 | 家長監控介面 |
| 👩‍🏫 教師端 | http://localhost:8083 | 教師管理介面 |
| 🔧 管理員 | http://localhost:8081 | 系統管理介面 |
| 📚 API 文檔 | http://localhost:8001/docs | 認證服務 API |
| 📖 題庫 API | http://localhost:8002/docs | 題庫服務 API |

### 測試帳號
```
學生帳號: student@test.com / password123
家長帳號: parent@test.com / password123  
教師帳號: teacher@test.com / password123
管理員帳號: admin@test.com / password123
```

---

## 🏗️ 系統架構

### 微服務架構
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   學生端應用     │    │   家長端應用     │    │   教師端應用     │
│   (Port 8080)   │    │   (Port 8082)   │    │   (Port 8083)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  API Gateway    │
                    │  (Nginx:80)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   認證服務       │    │   題庫服務       │    │   學習服務       │
│   (Port 8001)   │    │   (Port 8002)   │    │   (Port 8003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
              ┌─────────────────────────────────┐
              │          資料層                  │
              │  PostgreSQL │ MongoDB │ Redis  │
              └─────────────────────────────────┘
```

### 技術棧
- **後端**: Python + FastAPI + Uvicorn
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **資料庫**: PostgreSQL + MongoDB + Redis + MinIO
- **容器化**: Docker + Docker Compose
- **API Gateway**: Nginx
- **AI 整合**: Google Gemini API + CrewAI

---

## 📊 功能完成度

### ✅ 已完成功能 (95%)

#### 🔐 會員系統 (100%)
- JWT 認證機制
- 多角色註冊/登入
- 用戶資料管理
- 權限控制

#### 📚 學習系統 (100%)
- 條件式題目搜索
- 隨機出題功能
- 學習會話管理
- 即時自動批改
- 詳解與錯誤分析
- 學習記錄追蹤

#### 💾 資料管理 (100%)
- PostgreSQL 用戶資料
- MongoDB 題庫資料
- Redis 快取機制
- MinIO 檔案儲存

#### 🖥️ 前端應用 (90%)
- ✅ 學生端 (100% 完成)
- 🔄 家長端 (架構完成)
- 🔄 教師端 (架構完成)
- 🔄 管理員端 (架構完成)

### 🔄 待完善功能 (5%)
- AI 分析服務優化
- 家長教師儀表板完善
- 生產環境部署配置
- 進階用戶體驗優化

---

## 🧪 測試與驗證

### 功能測試
```bash
# 運行完整學習流程測試
python3 test_learning_flow.py

# 運行系統整合測試
python3 test_stage3_integration.py

# 運行前端流程測試
python3 test_frontend_flow.py
```

### 健康檢查
```bash
# 檢查所有服務狀態
curl http://localhost:8001/health  # 認證服務
curl http://localhost:8002/health  # 題庫服務

# 檢查容器狀態
docker compose ps
```

---

## 📁 專案結構

```
InULearning_V1/
├── 📁 2_implementation/
│   ├── 📁 backend/                    # 後端微服務
│   │   ├── 📁 auth-service/           # 認證服務
│   │   ├── 📁 question-bank-service/  # 題庫服務
│   │   ├── 📁 learning-service/       # 學習服務
│   │   └── 📁 shared/                 # 共用組件
│   ├── 📁 frontend/                   # 前端應用
│   │   ├── 📁 student-app/            # 學生端
│   │   ├── 📁 parent-app/             # 家長端
│   │   ├── 📁 teacher-app/            # 教師端
│   │   └── 📁 admin-app/              # 管理員端
│   └── 📁 database/                   # 資料庫配置
├── 📁 init-scripts/                   # 初始化腳本
├── 📁 nginx/                          # API Gateway
├── 📄 docker-compose.yml              # 容器編排
├── 📄 start.sh                        # 啟動腳本
├── 📄 stop.sh                         # 停止腳本
└── 📄 README.md                       # 專案說明
```

---

## 🔧 管理指令

### 系統控制
```bash
# 啟動系統
./start.sh

# 停止系統
./stop.sh

# 重新建置容器
docker compose build --no-cache

# 查看服務狀態
docker compose ps

# 查看服務日誌
docker compose logs -f [服務名]
```

### 資料庫管理
```bash
# 連接 PostgreSQL
docker exec -it inulearning_postgres psql -U aipe-tester -d inulearning

# 連接 MongoDB
docker exec -it inulearning_mongodb mongosh -u aipe-tester -p aipe-tester

# 連接 Redis
docker exec -it inulearning_redis redis-cli
```

---

## 🚨 故障排除

### 常見問題

#### 1. 端口被佔用
```bash
# 檢查端口使用狀況
sudo netstat -tulpn | grep :8080

# 修改 docker-compose.yml 中的端口映射
```

#### 2. 服務啟動失敗
```bash
# 查看詳細錯誤日誌
docker compose logs [服務名]

# 重新建置特定服務
docker compose build [服務名]
```

#### 3. 資料庫連接失敗
```bash
# 重新啟動資料庫服務
docker compose restart postgres mongodb redis

# 檢查資料庫健康狀態
docker compose ps
```

### 完全重置
```bash
# 停止並清除所有容器和資料
docker compose down -v
docker system prune -f

# 重新啟動
./start.sh
```

---

## 📈 專案統計

- **專案大小**: 56MB (已優化)
- **服務數量**: 7 個微服務
- **API 端點**: 50+ 個
- **前端頁面**: 20+ 個
- **資料表**: 11 個核心表
- **測試覆蓋**: 16 個測試檔案

---

## 🤝 開發團隊

**開發團隊**: AIPE01_group2  
**專案版本**: v3.0  
**最後更新**: 2024-12-29

---

## 📄 相關文檔

- [專案工作分解結構 (WBS)](WBS_CHECKLIST.md)
- [專案清理報告](PROJECT_CLEANUP_REPORT.md)
- [Docker 部署指南](README_DOCKER.md)
- [快速開始指南](QUICK_START.md)
- [測試指南](TESTING_GUIDE.md)

---

**🎉 專案狀態**: ✅ **核心功能完成，系統穩定運行，可進入下一階段開發** 