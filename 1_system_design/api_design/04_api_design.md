# API 設計規範 (API Design Specification) - InULearning 個人化學習平台

---

**文件版本 (Document Version):** `v1.1.0`

**最後更新 (Last Updated):** `2024-12-19`

**主要作者/設計師 (Lead Author/Designer):** `AIPE01_group2`

**審核者 (Reviewers):** `AIPE01_group2 團隊成員、技術架構師`

**狀態 (Status):** `草稿 (Draft)`

**相關 SD 文檔:** `03_system_design_document.md`

**OpenAPI/Swagger 定義文件:** `待建立`

---

## 目錄 (Table of Contents)

1.  [引言 (Introduction)](#1-引言-introduction)
2.  [通用設計約定 (General Design Conventions)](#2-通用設計約定-general-design-conventions)
3.  [認證與授權 (Authentication and Authorization)](#3-認證與授權-authentication-and-authorization)
4.  [錯誤處理 (Error Handling)](#4-錯誤處理-error-handling)
5.  [速率限制與配額 (Rate Limiting and Quotas)](#5-速率限制與配額-rate-limiting-and-quotas)
6.  [API 端點詳述 (API Endpoint Definitions)](#6-api-端點詳述-api-endpoint-definitions)
7.  [資料模型/Schema 定義 (Data Models / Schema Definitions)](#7-資料模型schema-定義-data-models--schema-definitions)
8.  [安全性考量 (Security Considerations)](#8-安全性考量-security-considerations)
9.  [向後兼容性與棄用策略 (Backward Compatibility and Deprecation Policy)](#9-向後兼容性與棄用策略-backward-compatibility-and-deprecation-policy)
10. [附錄 (Appendices)](#10-附錄-appendices)

---

## 1. 引言 (Introduction)

### 1.1 目的 (Purpose)
為 InULearning 個人化學習平台的前端應用、第三方整合服務和未來的開發者提供一個統一、明確的 RESTful API 接口契約，支援學生學習、家長監控、教師管理三大核心業務場景。

### 1.2 目標讀者 (Target Audience)
- 前端開發團隊（學生端、家長端、教師端、管理後台）
- 移動應用開發者
- 第三方整合服務開發者
- API 後端實現團隊
- 測試工程師
- 技術文檔撰寫者

### 1.3 API 風格與原則 (API Style and Principles)
- **RESTful Architecture:** 遵循 REST 成熟度模型 Level 2，使用 HTTP 動詞表達操作語義
- **JSON-First:** 統一使用 JSON 格式進行數據交換
- **版本控制:** 採用 URL 路徑版本控制 (e.g., `/api/v1/`)
- **一致性:** 統一的命名約定、錯誤格式和回應結構

---

## 2. 通用設計約定 (General Design Conventions)

### 2.1 Base URL
- **開發環境:** `http://localhost:8000/api/v1`
- **測試環境:** `https://api-test.inulearning.com/api/v1`
- **生產環境:** `https://api.inulearning.com/api/v1`

### 2.2 HTTP 方法使用約定

| HTTP 方法 | 用途 | 範例 |
|-----------|------|------|
| `GET` | 讀取資源 | `GET /api/v1/users/123` |
| `POST` | 創建新資源 | `POST /api/v1/users` |
| `PUT` | 完整更新資源 | `PUT /api/v1/users/123` |
| `PATCH` | 部分更新資源 | `PATCH /api/v1/users/123` |
| `DELETE` | 刪除資源 | `DELETE /api/v1/users/123` |

---

## 3. 認證與授權 (Authentication and Authorization)

### 3.1 認證機制
採用 **JWT (JSON Web Token)** 進行使用者認證：

```http
Authorization: Bearer <JWT_TOKEN>
```

### 3.2 角色權限
- **學生 (student):** 只能存取自己的學習數據
- **家長 (parent):** 可查看關聯學生的學習數據
- **教師 (teacher):** 可管理班級和學生數據
- **管理員 (admin):** 具備系統管理權限

---

## 4. 錯誤處理 (Error Handling)

### 4.1 標準錯誤格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed for one or more fields",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2024-12-19T10:30:00Z",
    "trace_id": "abc123def456"
  }
}
```

---

## 5. 速率限制與配額 (Rate Limiting and Quotas)

### 5.1 速率限制
- **一般用戶:** 100 requests/minute
- **認證用戶:** 1000 requests/minute
- **AI 分析端點:** 10 requests/minute

---

## 6. API 端點詳述 (API Endpoint Definitions)

### 6.1 用戶認證 API

#### 6.1.1 用戶註冊
- **端點:** `POST /api/v1/auth/register`
- **描述:** 註冊新用戶帳戶
- **請求體:**
```json
{
  "email": "student@example.com",
  "password": "securepassword",
  "role": "student",
  "profile": {
    "name": "張小明",
    "grade": "8A"
  }
}
```

#### 6.1.2 用戶登入
- **端點:** `POST /api/v1/auth/login`
- **描述:** 用戶登入並獲取 JWT Token
- **請求體:**
```json
{
  "email": "student@example.com",
  "password": "securepassword"
}
```

### 6.2 學習管理 API

#### 6.2.1 開始練習會話
- **端點:** `POST /api/v1/learning/exercises`
- **描述:** 創建新的個人化練習會話
- **請求體:**
```json
{
  "grade": "8A",
  "subject": "數學",
  "publisher": "南一",
  "chapter": "1-1 一元一次方程式",
  "question_count": 10,
  "difficulty": "normal"
}
```

#### 6.2.2 提交練習答案
- **端點:** `POST /api/v1/learning/sessions/{session_id}/submit`
- **描述:** 提交練習答案並獲得批改結果

---

## 7. 資料模型/Schema 定義 (Data Models / Schema Definitions)

### 7.1 用戶模型 (User Model)
```json
{
  "id": "uuid",
  "email": "string",
  "role": "student|parent|teacher|admin",
  "profile": {
    "name": "string",
    "grade": "string",
    "school": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 7.2 練習會話模型 (Exercise Session Model)
```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "grade": "string",
  "subject": "string",
  "publisher": "string",
  "questions": [],
  "start_time": "datetime",
  "status": "active|completed|abandoned"
}
```

---

## 8. 安全性考量 (Security Considerations)

### 8.1 數據驗證
- 所有輸入參數使用 Pydantic 模型進行嚴格驗證
- 防止 SQL 注入和 XSS 攻擊

### 8.2 數據加密
- 使用 HTTPS 進行數據傳輸加密
- 敏感數據在資料庫中加密存儲

---

## 9. 向後兼容性與棄用策略 (Backward Compatibility and Deprecation Policy)

### 9.1 版本管理
- API 版本通過 URL 路徑管理 (`/api/v1/`, `/api/v2/`)
- 舊版本 API 至少維護 6 個月

---

## 10. 附錄 (Appendices)

### 10.1 狀態碼對照表

| 狀態碼 | 描述 |
|-------|------|
| 200 | 請求成功 |
| 201 | 資源創建成功 |
| 400 | 請求參數錯誤 |
| 401 | 未認證 |
| 403 | 權限不足 |
| 404 | 資源不存在 |
| 500 | 服務器內部錯誤 |

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要/主要反饋 |
| :--------- | :--------- | :--- | :---------------------------------------------- |
| 2024-12-19 | AIPE01_group2 | v1.1.0 | API 設計規範初版，覆蓋主要業務場景 | 