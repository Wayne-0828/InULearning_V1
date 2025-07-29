# 需求追溯矩陣 (Requirements Traceability Matrix) - InULearning 個人化學習平台

---

**文件版本 (Document Version):** `v1.0.0`

**最後更新 (Last Updated):** `2024-12-19`

**主要作者 (Lead Author):** `AIPE01_group2`

**審核者 (Reviewers):** `AIPE01_group2 團隊成員`

**狀態 (Status):** `草稿 (Draft)`

**相關文檔 (Related Documents):**
*   專案摘要文檔: `00_project_summary.md`
*   使用者故事清單: `user_stories/user_stories.md`
*   系統架構文檔: `../1_system_design/architecture/02_system_architecture_document.md`

---

## 目錄 (Table of Contents)

1. [概述 (Overview)](#1-概述-overview)
2. [需求來源對照 (Requirements Source Mapping)](#2-需求來源對照-requirements-source-mapping)
3. [功能需求追溯 (Functional Requirements Traceability)](#3-功能需求追溯-functional-requirements-traceability)
4. [非功能需求追溯 (Non-Functional Requirements Traceability)](#4-非功能需求追溯-non-functional-requirements-traceability)
5. [測試案例對照 (Test Case Mapping)](#5-測試案例對照-test-case-mapping)
6. [需求變更追蹤 (Requirements Change Tracking)](#6-需求變更追蹤-requirements-change-tracking)

---

## 1. 概述 (Overview)

### 1.1 目的 (Purpose)
建立業務需求、功能規格、設計文檔、實作程式碼及測試案例之間的追溯關係，確保所有需求都能被適當地實現和驗證。

### 1.2 追溯層級 (Traceability Levels)
- **Level 1**: 業務需求 → 功能需求
- **Level 2**: 功能需求 → 使用者故事
- **Level 3**: 使用者故事 → 設計規格
- **Level 4**: 設計規格 → 實作程式碼
- **Level 5**: 實作程式碼 → 測試案例

---

## 2. 需求來源對照 (Requirements Source Mapping)

### 2.1 業務需求來源
| 需求ID | 業務需求描述 | 來源文檔 | 優先級 | 狀態 |
|--------|-------------|----------|--------|------|
| BR-001 | 建立精準的學習診斷系統 | 專案提案報告 | P0 | 已確認 |
| BR-002 | 提供個人化學習治療方案 | 專案提案報告 | P0 | 已確認 |
| BR-003 | 優化親子溝通模式 | 專案提案報告 | P1 | 已確認 |
| BR-004 | 支援教師因材施教 | 專案提案報告 | P2 | 已確認 |

### 2.2 使用者角色對應
| 角色 | 主要業務需求 | 相關使用者故事 |
|------|-------------|---------------|
| 學生 | BR-001, BR-002 | US-001 ~ US-006 |
| 家長 | BR-003 | US-007, US-008 |
| 教師 | BR-004 | US-009, US-010 |
| 管理員 | BR-001 ~ BR-004 | US-011 |

---

## 3. 功能需求追溯 (Functional Requirements Traceability)

### 3.1 核心功能追溯矩陣

| 使用者故事 | 功能需求 | 系統組件 | API 端點 | 實作狀態 | 測試案例 |
|------------|----------|----------|----------|----------|----------|
| **US-001** | 會員系統管理 | 認證服務 | `/api/v1/auth/*` | 待開發 | TC-001 ~ TC-005 |
| **US-002** | 智慧出題系統 | 學習服務<br/>題庫服務 | `/api/v1/learning/exercises`<br/>`/api/v1/questions/*` | 待開發 | TC-006 ~ TC-010 |
| **US-003** | 自動批改功能 | 學習服務 | `/api/v1/learning/submit` | 待開發 | TC-011 ~ TC-015 |
| **US-004** | 相似題練習 | AI 分析服務<br/>學習服務 | `/api/v1/ai/recommendations`<br/>`/api/v1/learning/similar` | 待開發 | TC-016 ~ TC-020 |
| **US-005** | 學習歷程記錄 | 學習服務 | `/api/v1/learning/history` | 待開發 | TC-021 ~ TC-025 |
| **US-006** | AI 智慧化升級 | AI 分析服務 | `/api/v1/ai/analysis` | 待開發 | TC-026 ~ TC-030 |
| **US-007** | 家長儀表板 | 報表服務<br/>學習服務 | `/api/v1/reports/parent`<br/>`/api/v1/learning/trends` | 待開發 | TC-031 ~ TC-035 |
| **US-008** | AI 溝通建議 | AI 分析服務 | `/api/v1/ai/communication` | 待開發 | TC-036 ~ TC-040 |
| **US-009** | 班級儀表板 | 報表服務 | `/api/v1/reports/class` | 待開發 | TC-041 ~ TC-045 |
| **US-010** | 學生管理 | 認證服務<br/>學習服務 | `/api/v1/users/students`<br/>`/api/v1/learning/management` | 待開發 | TC-046 ~ TC-050 |
| **US-011** | 系統管理 | 所有服務 | `/api/v1/admin/*` | 待開發 | TC-051 ~ TC-055 |

### 3.2 資料庫設計對應

| 使用者故事 | 主要資料表 | 關聯資料表 | 設計文檔位置 |
|------------|------------|------------|--------------|
| US-001 | `users` | `user_profiles` | 系統設計文檔 3.3.1 |
| US-002, US-003 | `learning_sessions` | `learning_records` | 系統設計文檔 3.3.1 |
| US-004, US-006 | `weakness_analysis_history` | `learning_records` | 系統設計文檔 3.3.1 |
| US-005 | `learning_progress_snapshots` | `learning_sessions` | 系統設計文檔 3.3.1 |
| US-007, US-008 | `user_learning_profiles` | `weakness_analysis_history` | 系統設計文檔 3.3.1 |

---

## 4. 非功能需求追溯 (Non-Functional Requirements Traceability)

### 4.1 效能需求對應

| NFR ID | 需求描述 | 目標值 | 測試方法 | 實作組件 | 驗證狀態 |
|--------|----------|--------|----------|----------|----------|
| NFR-001 | API 響應時間 | P95 < 500ms | 負載測試 | 所有服務 | 待測試 |
| NFR-002 | 併發用戶支援 | 1000+ 用戶 | 壓力測試 | API Gateway<br/>微服務 | 待測試 |
| NFR-003 | 頁面載入時間 | < 3 秒 | 前端效能測試 | 前端應用 | 待測試 |

### 4.2 安全性需求對應

| NFR ID | 需求描述 | 實作方法 | 相關組件 | 驗證方法 |
|--------|----------|----------|----------|----------|
| NFR-004 | 資料傳輸加密 | HTTPS/TLS 1.3+ | API Gateway | 安全掃描 |
| NFR-005 | 身份驗證 | JWT + OAuth 2.0 | 認證服務 | 身份驗證測試 |
| NFR-006 | 資料加密存儲 | 資料庫加密 | PostgreSQL<br/>MongoDB | 加密驗證 |

### 4.3 可用性需求對應

| NFR ID | 需求描述 | 目標值 | 實作方法 | 監控方式 |
|--------|----------|--------|----------|----------|
| NFR-007 | 系統可用性 | 99.9% | 多副本部署<br/>負載均衡 | 監控系統 |
| NFR-008 | 故障恢復時間 | RTO < 4 小時 | 自動故障轉移 | 告警系統 |
| NFR-009 | 資料恢復點 | RPO < 1 小時 | 定期備份 | 備份監控 |

---

## 5. 測試案例對照 (Test Case Mapping)

### 5.1 功能測試對照

| 測試案例ID | 對應使用者故事 | 測試類型 | 測試範圍 | 執行狀態 |
|------------|----------------|----------|----------|----------|
| TC-001 | US-001 | 單元測試 | 用戶註冊功能 | 待執行 |
| TC-002 | US-001 | 單元測試 | 用戶登入功能 | 待執行 |
| TC-003 | US-001 | 整合測試 | 認證服務整合 | 待執行 |
| TC-006 | US-002 | 單元測試 | 題目生成邏輯 | 待執行 |
| TC-007 | US-002 | 整合測試 | 出題系統整合 | 待執行 |
| TC-011 | US-003 | 單元測試 | 答案批改邏輯 | 待執行 |
| TC-016 | US-004 | 單元測試 | 相似題推薦 | 待執行 |
| TC-021 | US-005 | 單元測試 | 學習記錄存儲 | 待執行 |

### 5.2 端到端測試對照

| E2E 測試案例 | 涵蓋使用者故事 | 測試場景 | 執行狀態 |
|-------------|----------------|----------|----------|
| E2E-001 | US-001, US-002, US-003 | 完整學習流程 | 待執行 |
| E2E-002 | US-001, US-007, US-008 | 家長監控流程 | 待執行 |
| E2E-003 | US-001, US-009, US-010 | 教師管理流程 | 待執行 |

---

## 6. 需求變更追蹤 (Requirements Change Tracking)

### 6.1 變更記錄

| 變更ID | 日期 | 變更類型 | 影響範圍 | 變更原因 | 狀態 |
|--------|------|----------|----------|----------|------|
| CR-001 | 2024-12-19 | 新增 | US-006 | AI 功能需求明確化 | 已批准 |
| CR-002 | 2024-12-19 | 修改 | NFR-001 | 效能需求調整 | 已批准 |

### 6.2 影響分析

| 變更ID | 影響的組件 | 估算工時 | 風險評估 | 緩解措施 |
|--------|------------|----------|----------|----------|
| CR-001 | AI 分析服務 | +32 小時 | 中等 | 分階段實作 |
| CR-002 | 所有服務 | +8 小時 | 低 | 效能測試強化 |

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要/主要反饋 |
| :--------- | :--------- | :--- | :---------------------------------------------- |
| 2024-12-19 | AIPE01_group2 | v1.0.0 | 需求追溯矩陣初版，建立完整的需求追溯關係 | 