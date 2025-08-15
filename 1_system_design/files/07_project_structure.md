# 專案檔案結構文檔 (Project Structure Document) - InULearning 個人化學習平台

---

**文件版本 (Document Version):** `v1.1.0`

**最後更新 (Last Updated):** `2024-07-26`

**主要作者 (Lead Author):** `AIPE01_group2`

**審核者 (Reviewers):** `AIPE01_group2 團隊成員、系統架構師`

**狀態 (Status):** `已實現 (Implemented)`

**相關設計文檔 (Related Design Documents):**
*   系統架構文檔 (SA): `02_system_architecture_document.md`
*   系統設計文檔 (SD): `03_system_design_document.md`
*   API 設計文檔: `04_api_design.md`

---

## 目錄 (Table of Contents)

1.  [概述 (Overview)](#1-概述-overview)
2.  [專案根目錄結構 (Project Root Structure)](#2-專案根目錄結構-project-root-structure)
3.  [核心模組詳解 (Core Modules Details)](#3-核心模組詳解-core-modules-details)
4.  [依賴管理 (Dependency Management)](#4-依賴管理-dependency-management)
5.  [開發階段對應 (Development Phase Mapping)](#5-開發階段對應-development-phase-mapping)
6.  [部署文件結構 (Deployment File Structure)](#6-部署文件結構-deployment-file-structure)
7.  [文檔組織 (Documentation Organization)](#7-文檔組織-documentation-organization)
8.  [專案統計資訊 (Project Statistics)](#8-專案統計資訊-project-statistics)

---

## 1. 概述 (Overview)

### 1.1 專案架構類型 (Project Architecture Type)
*   **架構風格**: 微服務架構 (Microservices) + 事件驅動架構 (Event-Driven)
*   **技術棧**: Python + FastAPI + PostgreSQL + MongoDB + Redis + Docker + AI/ML (CrewAI, LangChain, Gemini)
*   **專案規模**: 大型專案，預計 500+ 檔案，支援三大使用者角色及完整 AI 學習生態系

### 1.2 目錄組織原則 (Directory Organization Principles)
*   **階段性開發**: 按開發階段組織 - 需求分析、設計、實作、測試、部署
*   **微服務導向**: 按業務域分離 - 認證服務、學習服務、AI 服務等
*   **前後端分離**: 前端應用與後端 API 服務完全分離
*   **環境隔離**: 開發、測試、生產環境配置分離

### 1.3 命名約定 (Naming Conventions)
*   **目錄名稱**: 小寫字母，使用連字符分隔 (kebab-case)
*   **服務名稱**: 描述性名稱，以 -service 結尾
*   **API 路徑**: RESTful 命名，名詞複數形式
*   **配置檔案**: .env, docker-compose.yml, requirements.txt

---

## 2. 專案根目錄結構 (Project Root Structure)

### 2.1 整體目錄樹 (Overall Directory Tree)

```
InULearning/
├── 0_requirements_analysis/               # 需求分析階段
│
├── 1_system_design/                       # 系統設計階段
│   ├── files/
│   │   ├── 00_project_summary.md
│   │   ├── 02_system_architecture_document.md
│   │   ├── 03_system_design_document.md
│   │   ├── 04_api_design.md
│   │   └── 07_project_structure.md        # 本檔案
│   └── ...
│
├── 2_implementation/                      # ★ 核心實作階段
│   ├── backend/                          # ★ 後端微服務群
│   │   ├── auth-service/                 # 用戶認證服務
│   │   ├── learning-service/             # ★ 學習管理服務
│   │   ├── question-bank-service/        # 題庫管理服務
│   │   ├── ai-analysis-service/          # ★ AI 分析服務
│   │   ├── parent-dashboard-service/     # 家長儀表板服務 (規劃中)
│   │   ├── teacher-management-service/   # 教師管理服務 (規劃中)
│   │   ├── notification-service/         # 通知服務 (規劃中)
│   │   ├── report-service/              # 報表服務 (規劃中)
│   │   └── shared/                      # 共用組件
│   │
│   ├── frontend/                        # ★ 前端應用群
│   │   ├── student-app/                 # 學生端應用
│   │   ├── parent-app/                  # 家長端應用
│   │   ├── teacher-app/                 # 教師端應用
│   │   ├── admin-app/                   # 管理後台應用
│   │   └── shared/                      # 前端共用資源
│   │
│   └── database/                        # 資料庫相關 (遷移、種子資料)
│
├── 3_testing/                           # 測試驗證階段
│
├── 4_deployment/                        # ★ 部署上線階段
│
├── config/                              # 全域配置 (移至根目錄)
│
├── docs/                                # ★ 技術文檔 (移至根目錄)
│
├── nginx/                               # Nginx 配置 (移至根目錄)
│
├── rawdata/                             # 原始數據
│
├── scripts/                             # 專案腳本
│
├── .gitignore                           # Git 忽略檔案
├── .env.example                         # 環境變數範本
├── docker-compose.yml                   # 主要容器編排
├── requirements.txt                     # Python 全域依賴
└── README.md                            # 專案主 README
```

### 2.2 目錄命名約定 (Directory Naming Conventions)
*   **階段式目錄**: 使用數字前綴表示開發階段 (0_, 1_, 2_, 3_, 4_)
*   **服務目錄**: 使用連字符命名，以 -service 結尾
*   **前端應用**: 使用連字符命名，以 -app 結尾
*   **語言約定**: 英文小寫，使用連字符或底線

---

## 3. 核心模組詳解 (Core Modules Details)

### 3.1 學習管理服務 (`backend/learning-service/`)

| 檔案/目錄 | 用途 | 主要功能/特性 |
|-----------|------|---------------|
| `main.py` | 服務入口點 | FastAPI 應用初始化、路由註冊 |
| `routers/exercises.py` | 練習管理 API | 創建練習、提交答案、批改結果 |
| `routers/sessions.py` | 學習會話 API | 會話列表、詳情查詢、歷程追蹤 |
| `routers/recommendations.py` | 推薦 API | 個人化學習建議、相似題推薦 |
| `models/learning_session.py` | 學習會話模型 | SQLAlchemy 資料模型定義 |
| `services/exercise_service.py` | 練習業務邏輯 | 出題邏輯、答案驗證、分數計算 |
| `services/analytics_service.py` | 學習分析服務 | 弱點分析、進度計算、趨勢分析 |

### 3.2 AI 分析服務 (`backend/ai-analysis-service/`)

| 檔案/目錄 | 用途 | 主要功能/特性 |
|-----------|------|---------------|
| `ai_agents/analyst_agent.py` | 分析師 Agent | CrewAI Agent，負責學習弱點分析 |
| `ai_agents/tutor_agent.py` | 導師 Agent | CrewAI Agent，提供學習指導建議 |
| `ai_agents/recommender_agent.py` | 推薦 Agent | CrewAI Agent，生成個人化推薦 |
| `services/crew_ai_service.py` | CrewAI 協作服務 | 多 Agent 協作編排和管理 |
| `services/langchain_service.py` | LangChain 服務 | LLM 鏈式處理和提示管理 |
| `services/gemini_service.py` | Gemini API 服務 | Google Gemini 模型呼叫和管理 |

### 3.3 題庫管理服務 (`backend/question-bank-service/`)

| 檔案/目錄 | 用途 | 主要功能/特性 |
|-----------|------|---------------|
| `routers/questions.py` | 題目管理 API | 題目 CRUD、批量匯入、多媒體檔案關聯 |
| `routers/files.py` | 檔案管理 API | MinIO 檔案上傳、下載、刪除管理 |
| `models/question.py` | 題目資料模型 | MongoDB 文檔模型，包含多媒體URL欄位 |
| `models/file.py` | 檔案資料模型 | 檔案元數據管理，MinIO 檔案關聯 |
| `services/question_service.py` | 題目業務邏輯 | 題目分類、搜尋、版本控制 |
| `services/file_service.py` | 檔案服務 | MinIO 檔案操作、URL 生成、存取權限 |
| `services/minio_client.py` | MinIO 客戶端 | 對象儲存連接、桶管理、檔案操作 |

### 3.4 前端學生應用 (`frontend/student-app/`)

| 檔案/目錄 | 用途 | 主要功能/特性 |
|-----------|------|---------------|
| `js/main.js` | 主要 JavaScript | 應用初始化、路由管理、狀態管理 |
| `js/api/` | API 呼叫模組 | 封裝所有後端 API 呼叫 |
| `js/components/` | UI 組件 | 可重用的 UI 組件（練習、結果展示等） |
| `pages/exercise.html` | 練習頁面 | 題目展示、答題介面、計時器 |
| `pages/results.html` | 結果頁面 | 成績展示、詳解查看、錯題分析 |
| `pages/dashboard.html` | 儀表板 | 學習進度、弱點分析、推薦練習 |

### 3.4 資料庫遷移和種子資料 (`database/`)

| 檔案/目錄 | 用途 | 執行方式 |
|-----------|------|----------|
| `migrations/postgresql/` | PostgreSQL 遷移 | `python manage.py migrate` |
| `migrations/mongodb/` | MongoDB 遷移 | `python mongo_migrate.py` |
| `seeds/users.sql` | 使用者種子資料 | `psql -f seeds/users.sql` |
| `seeds/questions.json` | 題目種子資料 | `mongoimport --file questions.json` |

### 3.5 配置和設置檔案 (Configuration Files)

| 檔案 | 用途 | 格式 |
|------|------|------|
| `requirements.txt` | Python 依賴管理 | pip freeze 格式 |
| `docker-compose.yml` | 容器編排配置 | YAML 格式 |
| `.env.example` | 環境變數範本 | KEY=VALUE 格式 |
| `config/environments/` | 環境配置檔案 | JSON/YAML 格式 |
| `config/database/` | 資料庫服務配置 | 各資料庫專用格式 |

---

## 4. 依賴管理 (Dependency Management)

### 4.1 Python 後端依賴 (`requirements.txt`)
```text
fastapi==0.104.1                    # 高效能 Web 框架
uvicorn==0.24.0                     # ASGI 伺服器
sqlalchemy==2.0.23                  # Python SQL 工具包
alembic==1.13.0                     # 資料庫遷移工具
psycopg2-binary==2.9.9              # PostgreSQL 適配器
pymongo==4.6.0                      # MongoDB 驅動
redis==5.0.1                        # Redis 客戶端
celery==5.3.4                       # 分散式任務佇列
pydantic==2.5.0                     # 資料驗證
langchain==0.1.0                    # LLM 應用框架
crewai==0.1.0                       # AI Agent 協作框架
google-generativeai==0.3.2          # Google Gemini API
```

### 4.2 AI/ML 相關依賴
```text
numpy==1.24.3                       # 數值計算
pandas==2.0.3                       # 資料分析
scikit-learn==1.3.0                 # 機器學習
pymilvus==2.3.4                     # Milvus 向量資料庫客戶端
minio==7.2.0                        # MinIO 對象儲存客戶端
langfuse==2.0.0                     # LLM 監控
ragas==0.1.0                        # RAG 評估框架
```

### 4.3 開發依賴 (Development Dependencies)
```text
pytest==7.4.3                       # 測試框架
pytest-asyncio==0.21.1              # 異步測試支援
black==23.11.0                      # 代碼格式化
flake8==6.1.0                       # 代碼風格檢查
mypy==1.7.1                         # 靜態類型檢查
coverage==7.3.2                     # 測試覆蓋率
```

### 4.4 依賴管理策略 (Dependency Management Strategy)
*   **版本鎖定**: 使用 requirements.txt 鎖定確切版本，確保環境一致性
*   **安全更新**: 使用 pip-audit 進行依賴安全掃描，定期更新有安全漏洞的套件
*   **許可證合規**: 使用 pip-licenses 檢查開源許可證，確保商業使用合規性
*   **虛擬環境**: 每個微服務使用獨立的 Python 虛擬環境

---

## 5. 開發階段對應 (Development Phase Mapping)

| 開發階段 | 目錄 | 狀態 | 主要交付物 | 預計時程 |
|----------|------|------|------------|----------|
| Phase 0: 需求分析 | `0_requirements_analysis/` | ✅ 完成 | 需求文檔、使用者故事、專案簡報 | Month 1 |
| Phase 1: 系統設計 | `1_system_design/` | ✅ 完成 | 架構文檔、API 設計、資料模型設計 | Month 2 |
| Phase 2.1: MVP 核心開發 | `2_implementation/backend/` | ✅ 完成 | 認證服務、學習服務、基礎 AI 功能 | Month 3-6 |
| Phase 2.2: 前端開發 | `2_implementation/frontend/` | ✅ 完成 | 學生端、家長端、教師端應用 | Month 4-6 |
| Phase 2.3: AI 進階功能 | `2_implementation/backend/ai-*` | 🔄 進行中 | 高級分析、個人化推薦、多 Agent 協作 | Month 6-8 |
| Phase 3: 測試驗證 | `3_testing/` | 🔄 進行中 | 單元測試、整合測試、效能測試 | Month 7-9 |
| Phase 4: 部署上線 | `4_deployment/` | 🔄 進行中 | 容器化、CI/CD、監控系統 | Month 9-10 |

---

## 6. 部署文件結構 (Deployment File Structure)

### 6.1 容器化配置檔案 (Containerization Configuration Files)
*   **開發環境**: `4_deployment/docker/docker-compose.dev.yml` (本地開發，包含熱重載)
*   **測試環境**: `4_deployment/docker/docker-compose.staging.yml` (模擬生產環境)
*   **生產環境**: `4_deployment/docker/docker-compose.prod.yml` (高可用性配置)

### 6.2 Kubernetes 部署配置 (K8s Deployment Configuration)
*   **命名空間**: `4_deployment/kubernetes/namespaces/` (環境隔離)
*   **服務發現**: `4_deployment/kubernetes/services/` (內部服務通信)
*   **負載均衡**: `4_deployment/kubernetes/ingress/` (外部流量路由)

### 6.3 基礎設施即代碼 (Infrastructure as Code)
*   **雲端資源**: `4_deployment/infrastructure/terraform/` (自動化資源建置)
*   **配置管理**: `4_deployment/infrastructure/ansible/` (系統配置自動化)
*   **監控配置**: `4_deployment/infrastructure/monitoring/` (可觀測性工具)

---

## 7. 文檔組織 (Documentation Organization)

### 7.1 設計文檔 (Design Documentation)
*   **專案摘要**: `files/00_project_summary.md` (專案概覽和目標)
*   **系統架構**: `files/02_system_architecture_document.md` (高層次架構設計)
*   **系統設計**: `files/03_system_design_document.md` (詳細設計規格)
*   **API 設計**: `files/04_api_design.md` (RESTful API 規格書)

### 7.2 技術文檔 (Technical Documentation)
*   **API 文檔**: `docs/api/openapi.yaml` (OpenAPI 規格)
*   **架構文檔**: `docs/architecture/` (技術架構詳述)
*   **部署指南**: `docs/deployment/` (部署和運維指南)

### 7.3 開發文檔 (Development Documentation)
*   **入門指南**: `docs/development/getting_started.md` (開發環境設置)
*   **編碼規範**: `docs/development/coding_standards.md` (代碼風格指南)
*   **測試指南**: `docs/development/testing_guide.md` (測試策略和工具)

---

## 8. 專案統計資訊 (Project Statistics)

### 8.1 當前專案規模統計
```
預計總檔案數量: 500+ 檔案
├── Python 源碼: 150+ 檔案 (~15,000 行)
│   ├── 後端服務: 120+ 檔案 (~12,000 行)
│   ├── AI 模組: 20+ 檔案 (~2,000 行)
│   └── 腳本工具: 10+ 檔案 (~1,000 行)
├── 前端代碼: 80+ 檔案 (~8,000 行)
│   ├── HTML 頁面: 20+ 檔案
│   ├── CSS 樣式: 30+ 檔案 (~3,000 行)
│   └── JavaScript: 30+ 檔案 (~5,000 行)
├── 配置檔案: 50+ 檔案
├── 文檔檔案: 20+ 檔案 (~10,000 行)
├── 測試檔案: 100+ 檔案 (~5,000 行)
└── 部署工具: 30+ 檔案 (~2,000 行)
```

### 8.2 服務複雜度統計 (Service Complexity Statistics)
*   **微服務數量**: 7 個核心服務
*   **API 端點數量**: 50+ 個 RESTful 端點
*   **資料庫表數量**: 15+ 個主要實體表
*   **AI 模型數量**: 3 個 CrewAI Agents
*   **前端應用數量**: 4 個獨立應用

### 8.3 技術債務評估 (Technical Debt Assessment)
*   **代碼覆蓋率目標**: 80%+ (目前建置中)
*   **技術債務等級**: 低 (新專案，採用現代技術棧)
*   **重構風險**: 低 (微服務架構，局部重構影響小)
*   **維護複雜度**: 中 (多服務協作，需要良好的監控)

---

## 📝 使用指南 (Usage Guide)

### 如何使用此專案結構 (How to Use This Project Structure)
1. **環境準備**: 根據 `docs/development/getting_started.md` 設置開發環境
2. **服務啟動**: 使用 `docker-compose up -d` 啟動所有服務
3. **開發流程**: 遵循 Git Flow，功能分支開發，代碼審查後合併
4. **測試執行**: 使用 `scripts/test/` 下的腳本執行各類測試
5. **部署流程**: 使用 `scripts/deploy/` 下的腳本進行部署

### 最佳實踐建議 (Best Practice Recommendations)
*   **保持同步**: 定期更新此文檔與實際專案結構同步
*   **服務獨立**: 每個微服務保持獨立性，避免直接資料庫訪問
*   **API 優先**: 所有服務間通信通過 RESTful API
*   **監控為先**: 建立完整的監控和告警機制
*   **文檔驅動**: 重要變更先更新文檔，再進行實作

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要/主要反饋 |
| :--------- | :--------- | :--- | :---------------------------------------------- |
| 2024-12-19 | AIPE01_group2 | v1.0.0 | 初稿完成，整合系統架構、API設計和系統設計文檔內容建立完整專案結構 |
| 2024-07-26 | AIPE01_group2 | v1.1.0 | 根據 v1.0 實際專案結構更新目錄樹，同步開發階段狀態，並將文件狀態更新為「已實現」。 | 