# InULearning 設計規格書（Design Specification）

## 1. 專案基本資訊
- **專案名稱**：InULearning（InU Learning）
- **框架與技術棧**：
  - 靜態前端（Nginx 部署）
  - 原生 HTML/CSS/JS
  - Tailwind CSS（登入/註冊頁使用 CDN 版）
  - Google Fonts（Noto Sans TC）
  - Material Icons
- **品牌視覺關鍵字**：藍色系、科技感、清爽明亮
- **目標使用者**：學生、家長、教師、管理員

---

## 2. 頁面與路由規範
### 全域頁面結構
- 首頁（`/`）包含品牌介紹、特色功能、應用入口、關於我們
- 登入與註冊頁為統一入口，支持多角色選擇與驗證
- 四個角色端獨立 Nginx 靜態站台（各自的 index.html）

### 路由與對應
| 頁面路由 | 頁面名稱 | 功能描述 | 導覽位置 |
|----------|----------|----------|----------|
| `/` | 首頁 | 品牌介紹、CTA、四端入口 | 主選單（錨點：特色功能、應用入口、關於我們） |
| `/login.html` | 統一登入頁 | 多角色登入、快速測試帳號 | 首頁右上角登入 |
| `/register.html` | 統一註冊頁 | 多角色註冊、強度提示與驗證 | 首頁右上角註冊 |
| `http://localhost:8080` | 學生端首頁 | 學生練功專區入口 | 首頁應用入口連結 |
| `http://localhost:8081` | 管理員端首頁 | 管理員控制台入口 | 首頁應用入口連結 |
| `http://localhost:8082` | 家長端首頁 | 家長關懷中心入口 | 首頁應用入口連結 |
| `http://localhost:8083` | 教師端首頁 | 教師工作台入口 | 首頁應用入口連結 |

---

## 3. 資訊架構（IA）
- **主選單項目（首頁）**：特色功能、應用入口、關於我們（錨點）+ 右上角登入/註冊  
  - 加入「文件/支援」連結到 FAQ 或指南
- **登入/註冊頁側邊欄**：品牌區 + 角色導覽，可補充平台優勢與示意圖
- **麵包屑**：首頁與登入/註冊頁不使用；子系統未來導入麵包屑

---

## 4. 色彩規範
- 主色（primary-blue）：`#3B82F6` → 主按鈕、重點字、邊框
- 輔色（accent-blue）：`#1E40AF` → 滑過狀態、強調陰影
- 文字深色（text-dark）：`#1F2937` → 標題與主要文字
- 文字淺色（text-light）：`#6B7280` → 次要說明文字（確保對比度）
- 淺藍背景（light-blue）：`#EFF6FF` → 區塊/圖示底色
- 更淺藍背景（lighter-blue）：`#F8FAFC` → 漸層背景

---

## 5. 字體與字級
- **字體**：`Noto Sans TC`（Google Fonts）
- **H1（首頁 Hero 標題）**：桌機 48/60、平板 40/52、手機 32/44
- **H2（區塊標題）**：桌機 32/44、手機 28/38
- **內文**：16/24
- **按鈕文字**：一般 16/24、大按鈕 18/28

---

## 6. 間距規範
- 區塊上下間距：桌機 64、平板 48、手機 32
- 卡片內外距：固定 24–32（行動裝置 16–24）
- 版面左右邊距：桌機 24、平板 20、手機 16

---

## 7. 元件規範
| 元件名稱 | 用途 | 狀態規範 |
|----------|------|----------|
| Navbar | 導覽/登入註冊入口 | hover 下劃線/變色；行動裝置改漢堡選單 |
| Primary Button (`.btn-primary`) | 主要操作 | hover 變深 + 陰影；補 `:focus-visible` 樣式 |
| Secondary Button (`.btn-secondary`) | 次要操作 | hover 反相 |
| Feature Card (`.feature-card`) | 說明特色 | hover 陰影；加鍵盤 focus 樣式 |
| App Card (`.app-card`) | 四端入口 | hover 陰影；可加角色徽章 |
| 表單輸入 | 表單填寫 | focus 邊框高亮；需有錯誤提示與 ARIA 屬性 |

---

## 8. 版型範本
- **Landing Page**：Navbar + Hero + Features + App Grid + Footer
- **Auth Page（登入/註冊）**：側邊品牌 + 頂部簡約頭 + 表單 + 提示  
  - 登入/註冊共用 JS 模組（錯誤訊息與驗證統一）

---

## 9. 響應式規範
- **手機（<480px）**：單欄、隱藏主選單、CTA 滿版、按鈕 100% 寬
- **平板（480–768px）**：單欄/雙欄混合、標題字級下修一階
- **桌機（>768px）**：多欄、最大寬度 1200px、內容區留白加大

---

## 10. 可及性（A11y）
- **對比度**：文字淺色需在白底達到 WCAG AA 標準
- **鍵盤操作**：所有可互動元素必須支援 tab 與明顯的 focus 樣式
- **ARIA 屬性**：表單欄位需有 `aria-invalid`、`aria-describedby`
- **Skip Link**：提供「跳到主要內容」的連結

---

## 11. SEO 與 Metadata
- 首頁：
  - Title：`InU Learning - 因你而學，學習只為你`
  - Meta Description：需補齊，並加入 OG 標籤
- 登入與註冊頁：
  - Title：對應頁面名稱
  - Meta Description：補齊描述
  - 視情況加入 `noindex`

---

## 12. 效能與最佳化
- 圖片使用 WebP/AVIF，設定尺寸屬性並 lazy load
- Tailwind 生產環境啟用 PurgeCSS，去除未用樣式
- 靜態資源長快取，HTML 禁快取
- 外部資源（Google Fonts/Icons）使用 `preconnect` 或合併載入

---

## 13. 測試與品質
- Lighthouse 四項（Performance/Accessibility/Best Practices/SEO）目標 ≥ 90
- 全專案使用 ESLint + Prettier（HTML/CSS/JS）
- 共用 JS 模組化管理（特別是登入/註冊驗證）

---

## 14. 前後端整合
- **API Gateway**：`http://localhost/api/v1/*`
  - Auth：`/api/v1/auth/*`
  - Relationships：`/api/v1/relationships/*`（由 auth-service 提供：教師-班級、學生-班級、親子關係）
  - Questions：`/api/v1/questions/*`
  - Learning：`/api/v1/learning/*`
  - AI：`/api/v1/ai/*`
- 登入成功後存 `access_token` 與 `user_info` 到 LocalStorage，並依角色跳轉：
  - 學生：`http://localhost:8080`
  - 家長：`http://localhost:8082`
  - 教師：`http://localhost:8083`
  - 管理員：`http://localhost:8081`

### 已完成的教師端功能（MVP 擴充）
- 班級管理（`/pages/classes.html`）
  - 功能：新增/編輯/刪除（Modal，驗證）、搜尋、科目篩選、排序（名稱/更新時間）、分頁（10/頁）
  - 學生管理：在「編輯」→「學生管理」分頁可搜尋、加入、移除學生
  - 導覽：列表僅顯示班級與科目；點「查看學生」導至 `students.html?class=...&classId=...`
  - API（實作於 auth-service/relationships）：
    - GET `/api/v1/relationships/teacher-class`（取得教師的授課班級）
    - POST `/api/v1/relationships/teacher-class/create-class`（教師一鍵建立班級並綁定科目）
    - PUT `/api/v1/relationships/teacher-class/{class_id}`（更新班級名稱/科目）
    - DELETE `/api/v1/relationships/teacher-class/{class_id}`（刪除授課班級，軟刪）
    - GET `/api/v1/relationships/classes/{class_id}/students`（班級學生列表）
    - POST `/api/v1/relationships/classes/{class_id}/students`（加入學生）
    - DELETE `/api/v1/relationships/classes/{class_id}/students/{student_id}`（移除學生）
    - GET `/api/v1/relationships/students/search?kw=...&limit=10`（學生搜尋）
  - 前端交互重點：
    - `classes.html` 改用科目篩選（`#subjectFilter`），學生數改為於細頁載入
    - `students.html` 支援 `?classId=`：若帶入則改呼叫 `/relationships/classes/{id}/students`
- 作業管理（`/pages/assignments.html`）
  - 列表搜尋/篩選/排序/分頁；快速建立與完整建立/編輯（Modal，含描述與題目 ID 列）、刪除
  - API（骨架）：
    - GET `/api/v1/learning/teacher/assignments`
    - POST `/api/v1/learning/teacher/assignments`
    - PUT `/api/v1/learning/teacher/assignments/{id}`
    - DELETE `/api/v1/learning/teacher/assignments/{id}`
- 題目管理（`/pages/questions.html`）
  - 新增/編輯/刪除（Modal），搜尋、科目/難度篩選、排序（更新/難度/題號）、分頁
  - API（骨架）：
    - GET `/api/v1/questions`
    - POST `/api/v1/questions`
    - PUT `/api/v1/questions/{id}`
    - DELETE `/api/v1/questions/{id}`
- 報告頁（`/pages/reports.html`）
  - 對齊後端端點並轉換資料：
    - 趨勢圖（進度圖）：GET `/api/v1/learning/trends/progress-chart?time_range=7d|30d|90d&subject=...`
    - 掌握度（取 radar normalized.knowledge_mastery）：GET `/api/v1/learning/analytics/subjects/radar?window=7d|30d|90d`
    - 科目比較（平均分數作為排行）：GET `/api/v1/learning/trends/subject-comparison?time_range=7d|30d|90d`
  - 篩選：班級、科目、日期區間（自動對應 window），支援匯出 CSV
  - 視覺：SVG 折線、conic 甜甜圈、橫向條形圖；含 skeleton 與空狀態

---

## 16. 後續建議
- 完善可及性（focus 樣式、ARIA、skip-link）
- 強化 SEO（meta description、OG/Twitter Card、結構化資料）
- 效能優化（Tailwind 本地打包、多語系切割）
- 設計系統化（色彩與字級 token、Storybook 元件庫）
- 共用 JS 模組化（auth、表單驗證）
