# 專案檔案結構文檔 (Project Structure Document) - InULearning 個人化學習平台

---

**文件版本 (Document Version):** `v1.0.0`

**最後更新 (Last Updated):** `2024-12-19`

**主要作者 (Lead Author):** `AIPE01_group2`

**審核者 (Reviewers):** `AIPE01_group2 團隊成員、系統架構師`

**狀態 (Status):** `草稿 (Draft)`

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
*   **模組檔案**: Python 模組使用下劃線分隔 (snake_case)
*   **配置檔案**: 使用 .env, .yaml, .json 等標準副檔名

---

## 2. 專案根目錄結構 (Project Root Structure)

```
InULearning/
├── README.md                           # 專案主要說明文檔
├── .gitignore                          # Git 忽略文件配置
├── .env.example                        # 環境變數範例檔案
├── docker-compose.yml                  # Docker 服務編排配置
├── docker-compose.dev.yml             # 開發環境 Docker 配置
├── docker-compose.prod.yml            # 生產環境 Docker 配置
├── pyproject.toml                      # Python 專案配置 (Poetry)
├── poetry.lock                         # 依賴版本鎖定檔案
├── Makefile                            # 常用命令腳本
│
├── 0_requirements_analysis/            # 需求分析階段文檔
│   ├── business_requirements/
│   ├── user_stories/
│   └── requirements_matrix/
│
├── 1_system_design/                    # 系統設計階段文檔
│   ├── architecture/
│   ├── detailed_design/
│   ├── api_design/
│   └── database_design/
│
├── 2_implementation/                   # 實作階段檔案
│   ├── backend/                        # 後端服務實作
│   ├── frontend/                       # 前端應用實作
│   └── shared/                         # 共用組件與工具
│
├── 3_testing/                          # 測試相關檔案
│   ├── unit_tests/
│   ├── integration_tests/
│   └── e2e_tests/
│
├── 4_deployment/                       # 部署相關檔案
│   ├── infrastructure/
│   ├── scripts/
│   └── monitoring/
│
├── docs/                               # 專案文檔
│   ├── api/
│   ├── development/
│   ├── deployment/
│   └── user_guides/
│
├── database/                           # 資料庫相關檔案
│   ├── migrations/
│   ├── seeds/
│   └── schemas/
│
└── tools/                             # 開發工具與腳本
    ├── scripts/
    ├── generators/
    └── validators/
```

---

## 3. 核心模組詳解 (Core Modules Details)

### 3.1 後端服務架構 (Backend Services Architecture)

```
2_implementation/backend/
├── auth-service/                       # 用戶認證服務
│   ├── app/
│   │   ├── api/                       # API 路由定義
│   │   ├── core/                      # 核心業務邏輯
│   │   ├── models/                    # 資料模型
│   │   ├── schemas/                   # Pydantic 資料模型
│   │   ├── services/                  # 業務服務層
│   │   └── utils/                     # 工具函數
│   ├── tests/                         # 服務測試
│   ├── Dockerfile                     # Docker 容器配置
│   ├── requirements.txt               # Python 依賴
│   └── main.py                        # 服務入口點
│
├── learning-service/                   # 學習管理服務
├── question-bank-service/              # 題庫管理服務
├── ai-analysis-service/                # AI 分析服務
├── notification-service/               # 通知服務
├── report-service/                     # 報表服務
└── shared/                            # 共用組件
    ├── database/                      # 資料庫連接配置
    ├── middleware/                    # 中介軟體
    ├── schemas/                       # 共用資料模型
    └── utils/                         # 共用工具函數
```

### 3.2 前端應用架構 (Frontend Applications Architecture)

```
2_implementation/frontend/
├── student-app/                        # 學生端應用
│   ├── assets/                        # 靜態資源
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── components/                    # 可重用組件
│   ├── pages/                         # 頁面文件
│   ├── services/                      # API 服務
│   ├── utils/                         # 工具函數
│   └── index.html                     # 主頁面
│
├── parent-app/                         # 家長端應用
├── teacher-app/                        # 教師端應用
├── admin-app/                          # 管理後台應用
└── shared/                            # 前端共用資源
    ├── components/                    # 共用組件
    ├── styles/                        # 共用樣式
    └── utils/                         # 共用 JavaScript 工具
```

---

## 4. 依賴管理 (Dependency Management)

### 4.1 Python 依賴管理 (Python Dependencies)
使用 **Poetry** 進行 Python 依賴管理：

```toml
# pyproject.toml
[tool.poetry]
name = "inulearning"
version = "0.1.0"
description = "InULearning 個人化學習平台"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
psycopg2-binary = "^2.9.0"
pymongo = "^4.6.0"
redis = "^5.0.0"
```

### 4.2 前端依賴管理 (Frontend Dependencies)
前端使用原生 HTML/CSS/JavaScript，依賴管理較為簡單：

```json
// package.json (如需要)
{
  "name": "inulearning-frontend",
  "version": "1.0.0",
  "devDependencies": {
    "http-server": "^14.1.1",
    "live-server": "^1.2.2"
  }
}
```

---

## 5. 開發階段對應 (Development Phase Mapping)

### 5.1 Phase 1: 需求分析與系統設計
```
0_requirements_analysis/
1_system_design/
docs/
```

### 5.2 Phase 2: 核心功能開發
```
2_implementation/backend/
2_implementation/frontend/
database/
```

### 5.3 Phase 3: 系統整合與部署
```
3_testing/
4_deployment/
tools/
```

---

## 6. 部署文件結構 (Deployment File Structure)

### 6.1 Docker 配置
```
docker-compose.yml                     # 主要服務編排
docker-compose.dev.yml                # 開發環境配置
docker-compose.prod.yml               # 生產環境配置

4_deployment/
├── infrastructure/
│   ├── nginx/                         # Nginx 配置
│   ├── postgres/                      # PostgreSQL 配置
│   └── monitoring/                    # 監控配置
├── scripts/
│   ├── deploy.sh                      # 部署腳本
│   ├── backup.sh                      # 備份腳本
│   └── health-check.sh                # 健康檢查腳本
└── k8s/                              # Kubernetes 配置 (後期)
```

---

## 7. 文檔組織 (Documentation Organization)

### 7.1 文檔分類
```
docs/
├── api/                               # API 文檔
│   ├── auth-api.md
│   ├── learning-api.md
│   └── openapi.yaml
├── development/                       # 開發文檔
│   ├── getting-started.md
│   ├── coding-standards.md
│   └── testing-guide.md
├── deployment/                        # 部署文檔
│   ├── docker-guide.md
│   ├── production-setup.md
│   └── monitoring-guide.md
└── user_guides/                      # 使用者指南
    ├── student-guide.md
    ├── parent-guide.md
    └── teacher-guide.md
```

---

## 8. 專案統計資訊 (Project Statistics)

### 8.1 預期檔案統計
*   **總檔案數**: ~500-600 個檔案
*   **Python 檔案**: ~200-250 個
*   **前端檔案**: ~150-200 個
*   **配置檔案**: ~50-80 個
*   **文檔檔案**: ~80-100 個

### 8.2 程式碼行數預估
*   **後端程式碼**: ~15,000-20,000 行
*   **前端程式碼**: ~8,000-12,000 行
*   **測試程式碼**: ~5,000-8,000 行
*   **總計**: ~28,000-40,000 行

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要/主要反饋 |
| :--------- | :--------- | :--- | :---------------------------------------------- |
| 2024-12-19 | AIPE01_group2 | v1.0.0 | 專案結構文檔初版，定義完整目錄組織架構 | 