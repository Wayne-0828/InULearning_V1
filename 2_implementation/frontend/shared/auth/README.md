# InU Learning 統一登入系統

## 概述

這是 InU Learning 系統的統一登入頁面，提供多角色用戶的集中認證功能。

## 功能特色

### 🔐 多角色支援
- **學生** (student) - 跳轉至學生應用 (8080)
- **家長** (parent) - 跳轉至家長應用 (8082)  
- **教師** (teacher) - 跳轉至教師應用 (8083)
- **管理員** (admin/manager) - 跳轉至管理員應用 (8081)

### 🚀 快速登入測試
提供測試帳號快速登入功能：
- 學生測試帳號: `student01@test.com` / `password123`
- 家長測試帳號: `parent01@test.com` / `password123`
- 教師測試帳號: `teacher01@test.com` / `password123`
- 管理員測試帳號: `admin01@test.com` / `password123`

### 🎨 現代化 UI
- 響應式設計，支援桌面和移動設備
- 使用 Tailwind CSS 框架
- Material Icons 圖標
- 流暢的動畫效果

## 檔案結構

```
frontend/shared/auth/
├── login.html          # 主要登入頁面
├── test-login.html     # 測試頁面
└── README.md          # 說明文件
```

## 技術實現

### 前端技術
- **HTML5** - 語義化標籤
- **CSS3** - Tailwind CSS 框架
- **JavaScript ES6+** - 模組化設計
- **Material Icons** - Google 圖標庫

### 核心功能
1. **身份選擇** - 用戶可選擇登入身份
2. **表單驗證** - 客戶端輸入驗證
3. **API 整合** - 與後端認證服務整合
4. **JWT 解析** - 解析用戶資訊和權限
5. **智能跳轉** - 根據用戶角色跳轉到對應應用

### 安全特性
- 密碼輸入遮罩
- CSRF 防護
- XSS 防護
- 安全的 JWT 處理

## 部署配置

### Docker 配置
在 `docker-compose.yml` 中已配置：
```yaml
volumes:
  - ./2_implementation/frontend/shared/auth/login.html:/usr/share/nginx/html/login.html
```

### 端口配置
- **學生應用**: `http://localhost:8080`
- **管理員應用**: `http://localhost:8081`
- **家長應用**: `http://localhost:8082`
- **教師應用**: `http://localhost:8083`

## 使用方式

### 1. 直接訪問
```
http://localhost/login.html
```

### 2. 通過 nginx 代理
```
http://localhost:80/login.html
```

### 3. 測試功能
```
http://localhost:80/test-login.html
```

## API 整合

### 登入 API
```javascript
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

### 回應格式
```javascript
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 開發指南

### 本地開發
1. 確保後端認證服務運行在 `localhost:8000`
2. 啟動 nginx 代理服務
3. 訪問 `http://localhost/login.html`

### 測試流程
1. 選擇用戶身份
2. 輸入測試帳號或真實帳號
3. 點擊登入按鈕
4. 系統會自動跳轉到對應的應用

### 除錯技巧
- 打開瀏覽器開發者工具
- 查看 Console 日誌
- 檢查 Network 標籤中的 API 請求
- 使用 `test-login.html` 進行功能測試

## 注意事項

1. **CORS 配置** - 確保後端服務已正確配置 CORS
2. **SSL 證書** - 生產環境建議使用 HTTPS
3. **Session 管理** - 注意 token 過期處理
4. **錯誤處理** - 提供友好的錯誤提示

## 更新日誌

- **v1.0.0** - 初始版本，支援基本登入功能
- **v1.1.0** - 新增快速登入測試功能
- **v1.2.0** - 優化 UI 設計和響應式佈局

## 聯絡資訊

如有問題或建議，請聯繫開發團隊。 