# InULearning 個人化學習平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 🎯 專案概述

**InULearning** 是一個 AI 驅動的個人化學習平台，旨在解決傳統教育模式的痛點，提供精準的學習診斷、個人化學習治療方案，並優化親子溝通模式。

### 🌟 核心特色

- **🤖 AI 智慧分析**: 使用 CrewAI + LangChain + Gemini 進行學習弱點分析
- **📊 個人化推薦**: 基於學習歷程提供客製化練習題和學習建議
- **👨‍👩‍👧‍👦 親子溝通優化**: 家長儀表板與 AI 溝通建議
- **📈 學習歷程追蹤**: 完整的學習數據分析和視覺化
- **🏗️ 微服務架構**: 高可擴展性、高可用性的系統設計

### 🎯 目標用戶

- **主要用戶**: 國中生（7-9年級）
- **次要用戶**: 家長、教師
- **管理用戶**: 系統管理員

## 🚀 快速開始

### 前置需求

- **Docker & Docker Compose**: 用於容器化部署
- **Python 3.11+**: 後端開發
- **Node.js 18+**: 前端開發（可選）
- **Git**: 版本控制

### 環境設置

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd InULearning_V1
   ```

2. **複製環境變數**
   ```bash
   cp env.example .env
   # 編輯 .env 檔案，填入實際的配置值
   ```

3. **啟動開發環境**
   ```bash
   # 啟動所有服務
   docker-compose -f 4_deployment/docker/docker-compose.dev.yml up -d
   
   # 或使用開發腳本
   ./2_implementation/scripts/setup/dev-setup.sh
   ```

4. **驗證服務狀態**
   ```bash
   # 檢查所有服務狀態
   docker-compose ps
   
   # 查看服務日誌
   docker-compose logs -f
   ```

### 開發環境訪問

- **API Gateway**: http://localhost:8000
- **學生端應用**: http://localhost:3000
- **家長端應用**: http://localhost:3001
- **教師端應用**: http://localhost:3002
- **管理後台**: http://localhost:3003
- **API 文檔**: http://localhost:8000/docs

## 🏗️ 系統架構

### 微服務架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端應用層     │    │   API Gateway   │    │   後端服務層     │
│                 │    │                 │    │                 │
│ • 學生端應用     │◄──►│ • Nginx         │◄──►│ • 認證服務      │
│ • 家長端應用     │    │ • 負載均衡      │    │ • 學習服務      │
│ • 教師端應用     │    │ • 路由管理      │    │ • 題庫服務      │
│ • 管理後台       │    │                 │    │ • AI 分析服務   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐            │
                       │   資料層        │            │
                       │                 │            │
                       │ • PostgreSQL    │◄───────────┘
                       │ • MongoDB       │
                       │ • Redis         │
                       │ • Milvus        │
                       │ • MinIO         │
                       └─────────────────┘
```

### 技術棧

| 層級 | 技術 | 用途 |
|------|------|------|
| **前端** | HTML5, CSS3, JavaScript | 響應式 Web 應用 |
| **API Gateway** | Nginx | 反向代理、負載均衡 |
| **後端框架** | FastAPI | 高效能 Web API |
| **資料庫** | PostgreSQL, MongoDB | 關聯式、文件式資料儲存 |
| **快取** | Redis | 會話管理、快取 |
| **向量資料庫** | Milvus | AI 相似度搜尋 |
| **檔案儲存** | MinIO | 對象儲存 |
| **訊息佇列** | RabbitMQ | 異步任務處理 |
| **AI/ML** | CrewAI, LangChain, Gemini | 智慧分析與推薦 |
| **容器化** | Docker, Docker Compose | 部署與編排 |
| **監控** | Prometheus, Grafana | 系統監控 |

## 📁 專案結構

```
InULearning_V1/
├── 0_requirements_analysis/     # 需求分析階段
├── 1_system_design/             # 系統設計階段
├── 2_implementation/            # 核心實作階段
│   ├── backend/                 # 後端微服務
│   │   ├── auth-service/        # 認證服務
│   │   ├── learning-service/    # 學習服務
│   │   ├── question-bank-service/ # 題庫服務
│   │   ├── ai-analysis-service/ # AI 分析服務
│   │   └── shared/              # 共用組件
│   ├── frontend/                # 前端應用
│   │   ├── student-app/         # 學生端
│   │   ├── parent-app/          # 家長端
│   │   └── teacher-app/         # 教師端
│   ├── database/                # 資料庫相關
│   └── scripts/                 # 開發腳本
├── 3_testing/                   # 測試驗證階段
├── 4_deployment/                # 部署上線階段
├── config/                      # 配置檔案
├── docs/                        # 技術文檔
├── tools/                       # 開發工具
└── files/                       # 專案文檔
```

## 🔧 開發指南

### 開發流程

1. **功能開發**
   ```bash
   # 建立功能分支
   git checkout -b feature/your-feature-name
   
   # 開發完成後提交
   git add .
   git commit -m "feat: add your feature description"
   
   # 推送到遠端
   git push origin feature/your-feature-name
   ```

2. **測試執行**
   ```bash
   # 執行單元測試
   pytest 3_testing/unit_tests/
   
   # 執行整合測試
   pytest 3_testing/integration_tests/
   
   # 執行 E2E 測試
   pytest 3_testing/e2e_tests/
   ```

3. **程式碼品質檢查**
   ```bash
   # 程式碼格式化
   black 2_implementation/backend/
   
   # 程式碼風格檢查
   flake8 2_implementation/backend/
   
   # 類型檢查
   mypy 2_implementation/backend/
   ```

### API 開發

- **API 文檔**: 查看 `docs/api/openapi.yaml`
- **Postman 集合**: 查看 `docs/api/postman_collections/`
- **API 測試**: 使用 `3_testing/integration_tests/api/`

### 資料庫操作

```bash
# 執行資料庫遷移
python -m alembic upgrade head

# 建立種子資料
python 2_implementation/scripts/setup/seed_data.py

# 備份資料庫
./2_implementation/database/scripts/backup.sh
```

## 🧪 測試策略

### 測試金字塔

```
    ┌─────────────┐
    │   E2E 測試   │  ← 端對端測試
    └─────────────┘
         │
    ┌─────────────┐
    │  整合測試    │  ← 服務間整合
    └─────────────┘
         │
    ┌─────────────┐
    │  單元測試    │  ← 基礎測試
    └─────────────┘
```

### 測試覆蓋率目標

- **單元測試**: ≥ 80%
- **整合測試**: ≥ 70%
- **E2E 測試**: 關鍵流程 100%

## 📊 監控與日誌

### 監控指標

- **系統指標**: CPU、記憶體、磁碟使用率
- **應用指標**: API 響應時間、錯誤率、吞吐量
- **業務指標**: 用戶活躍度、學習成效、留存率
- **AI 指標**: 模型準確度、推理時間、推薦相關度

### 日誌管理

- **結構化日誌**: JSON 格式，包含 trace ID
- **日誌等級**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **日誌輪轉**: 按大小和時間自動輪轉

## 🚀 部署

### 環境類型

- **開發環境**: 本地 Docker Compose
- **測試環境**: 雲端輕量級部署
- **生產環境**: 高可用 Kubernetes 部署

### 部署流程

```bash
# 1. 建置映像檔
docker-compose build

# 2. 執行測試
./2_implementation/scripts/test/run-all-tests.sh

# 3. 部署到測試環境
./4_deployment/scripts/deploy.sh staging

# 4. 部署到生產環境
./4_deployment/scripts/deploy.sh production
```

## 🤝 貢獻指南

### 開發規範

1. **程式碼風格**: 遵循 PEP 8 和 Black 格式化
2. **提交訊息**: 使用 Conventional Commits 格式
3. **分支策略**: Git Flow 工作流程
4. **程式碼審查**: 所有變更需要 PR 審查

### 提交訊息格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

範例：
```
feat(auth): add JWT token refresh endpoint

- Add refresh token validation
- Implement token blacklist mechanism
- Add unit tests for refresh flow

Closes #123
```

## 📚 文檔

- **系統架構**: `files/02_system_architecture_document.md`
- **API 設計**: `files/04_api_design.md`
- **專案結構**: `files/07_project_structure.md`
- **開發指南**: `docs/development/getting_started.md`
- **部署指南**: `docs/deployment/`

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 👥 團隊

- **專案團隊**: AIPE01_group2
- **技術架構師**: [待指派]
- **專案經理**: [待指派]

## 📞 聯絡資訊

- **專案問題**: 請使用 GitHub Issues
- **技術討論**: 請使用 GitHub Discussions
- **緊急聯絡**: [待提供]

---

**InULearning** - 讓學習更智慧，讓成長更精準 🚀 