# InULearning_V1 架構檢查與修正報告

**報告日期:** 2024-12-19  
**檢查範圍:** US-001, US-002, US-003, US-005, US-007, US-009  
**目標:** Docker Compose 完整整合，前後端及資料庫服務正常運作

---

## 1. 當前架構概況

### 1.1 項目結構分析
```
InULearning_V1/
├── 2_implementation/
│   ├── backend/
│   │   ├── auth-service/          ✅ 已建立
│   │   ├── question-bank-service/ ✅ 已建立
│   │   ├── learning-service/      ✅ 已建立
│   │   ├── ai-analysis-service/   ⚠️ 需要備註 (Milvus/RAG)
│   │   ├── notification-service/  ⚠️ 需要備註
│   │   ├── teacher-management-service/ ⚠️ 需要備註
│   │   ├── parent-dashboard-service/   ⚠️ 需要備註
│   │   ├── report-service/        ⚠️ 需要備註
│   │   └── api-gateway/           ✅ 已建立
│   └── frontend/
│       ├── student-app/           ✅ 已建立
│       ├── admin-app/             ✅ 已建立
│       ├── parent-app/            ✅ 已建立
│       └── teacher-app/           ✅ 已建立
├── rawdata/                       ✅ 題庫資料已準備
├── docker-compose.yml             ✅ 已建立
└── nginx/                         ✅ 已建立
```

### 1.2 Docker Compose 服務分析
**已配置服務:**
- ✅ PostgreSQL (5432)
- ✅ MongoDB (27017)
- ✅ Redis (6379)
- ✅ MinIO (9000/9001)
- ✅ Auth Service (8001)
- ✅ Question Bank Service (8002)
- ✅ Learning Service (8003)
- ✅ Nginx Gateway (80)
- ✅ Student Frontend (8080)

**缺失服務:**
- ❌ Admin Frontend
- ❌ Parent Frontend  
- ❌ Teacher Frontend
- ❌ AI Analysis Service (需備註)
- ❌ 其他後端服務 (需備註)

---

## 2. 主要問題識別

### 2.1 前端服務缺失
**問題:** Docker Compose 中只配置了 student-frontend，缺少 admin、parent、teacher 前端服務
**影響:** 無法完整測試 US-007 (家長監控) 和 US-009 (教師管理)
**解決方案:** 添加缺失的前端服務配置

### 2.2 後端服務過度配置
**問題:** 配置了過多後端服務，但部分服務 (AI分析、通知等) 需要備註
**影響:** 增加系統複雜度，可能導致啟動失敗
**解決方案:** 暫時註釋掉不需要的服務，專注於核心功能

### 2.3 章節動態載入問題
**問題:** exercise.js 中的章節載入邏輯需要整合 `三版本科目章節.json`
**影響:** 無法正確顯示章節選項
**解決方案:** 修改前端邏輯，整合靜態章節資料

### 2.4 會員系統整合問題
**問題:** 前端認證邏輯需要與後端 auth-service 完全整合
**影響:** 登入/註冊功能可能無法正常工作
**解決方案:** 確保前後端 API 對接正確

### 2.5 資料庫初始化問題
**問題:** 需要確保 MongoDB 題庫資料正確載入
**影響:** 練習功能無法正常運作
**解決方案:** 完善資料庫初始化腳本

---

## 3. 修正計劃

### 3.1 Docker Compose 修正
**目標:** 簡化服務配置，專注於核心功能

**修正內容:**
1. 註釋掉 AI Analysis Service (Milvus/RAG 相關)
2. 註釋掉 Notification Service
3. 註釋掉 Teacher Management Service
4. 註釋掉 Parent Dashboard Service
5. 註釋掉 Report Service
6. 添加缺失的前端服務 (admin, parent, teacher)
7. 確保服務依賴關係正確

### 3.2 前端整合修正
**目標:** 統一前端設計，整合章節資料

**修正內容:**
1. 修改 exercise.js 整合 `三版本科目章節.json`
2. 確保所有前端應用使用相同的設計風格
3. 完善認證邏輯整合
4. 添加錯誤處理和用戶反饋

### 3.3 後端服務修正
**目標:** 確保核心服務正常運作

**修正內容:**
1. 驗證 auth-service API 端點
2. 驗證 question-bank-service 資料載入
3. 驗證 learning-service 業務邏輯
4. 確保服務間通訊正常

### 3.4 資料庫修正
**目標:** 確保資料正確初始化

**修正內容:**
1. 完善 MongoDB 初始化腳本
2. 確保題庫資料正確載入
3. 驗證 PostgreSQL 用戶表結構
4. 添加測試資料

---

## 4. 具體修正步驟

### 4.1 第一步：Docker Compose 簡化
```yaml
# 需要註釋的服務
# ai-analysis-service:  # 備註 - Milvus/RAG 後續開發
# notification-service: # 備註 - 後續開發
# teacher-management-service: # 備註 - 後續開發
# parent-dashboard-service: # 備註 - 後續開發
# report-service: # 備註 - 後續開發

# 需要添加的前端服務
admin-frontend:
  build:
    context: ./2_implementation/frontend
    dockerfile: admin-app/Dockerfile
  container_name: inulearning_admin_frontend
  ports:
    - "8081:80"
  environment:
    - API_BASE_URL=http://localhost/api
  depends_on:
    - nginx
  networks:
    - inulearning_network

parent-frontend:
  build:
    context: ./2_implementation/frontend
    dockerfile: parent-app/Dockerfile
  container_name: inulearning_parent_frontend
  ports:
    - "8082:80"
  environment:
    - API_BASE_URL=http://localhost/api
  depends_on:
    - nginx
  networks:
    - inulearning_network

teacher-frontend:
  build:
    context: ./2_implementation/frontend
    dockerfile: teacher-app/Dockerfile
  container_name: inulearning_teacher_frontend
  ports:
    - "8083:80"
  environment:
    - API_BASE_URL=http://localhost/api
  depends_on:
    - nginx
  networks:
    - inulearning_network
```

### 4.2 第二步：前端章節整合
```javascript
// exercise.js 修正
async loadChaptersFromAPI(grade, edition, subject) {
    try {
        // 優先使用靜態資料
        const staticChapters = this.getStaticChapters(grade, edition, subject);
        if (staticChapters && staticChapters.length > 0) {
            return staticChapters;
        }
        
        // 備用 API 載入
        const response = await fetch(`/api/question-bank/chapters?grade=${grade}&edition=${edition}&subject=${subject}`);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('載入章節失敗:', error);
    }
    return [];
}

getStaticChapters(grade, edition, subject) {
    // 整合三版本科目章節.json 的資料
    const chaptersData = window.chaptersData || [];
    const match = chaptersData.find(item => 
        item.出版社 === edition && 
        item.科目 === subject
    );
    
    if (match && match.年級章節[grade]) {
        return match.年級章節[grade];
    }
    return [];
}
```

### 4.3 第三步：資料庫初始化
```javascript
// init-mongodb.js 修正
db = db.getSiblingDB('inulearning');

// 載入題庫資料
const questionFiles = [
    'sample_questions.json',
    '南一_7A_自然.json',
    '南一_國文.json',
    '生成_數學_100.json',
    '翰林(公民).json',
    '翰林(地理).json',
    '翰林(歷史).json',
    '翰林(自然).json'
];

questionFiles.forEach(file => {
    const questions = JSON.parse(cat('/docker-entrypoint-initdb.d/rawdata/' + file));
    db.questions.insertMany(questions);
});

// 建立索引
db.questions.createIndex({ "grade": 1, "subject": 1, "publisher": 1 });
db.questions.createIndex({ "chapter": 1 });
db.questions.createIndex({ "difficulty": 1 });
```

### 4.4 第四步：API Gateway 配置
```nginx
# nginx.conf 修正
upstream auth_service {
    server auth-service:8000;
}

upstream question_bank_service {
    server question-bank-service:8000;
}

upstream learning_service {
    server learning-service:8000;
}

server {
    listen 80;
    server_name localhost;

    # API 路由
    location /api/auth/ {
        proxy_pass http://auth_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/question-bank/ {
        proxy_pass http://question_bank_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/learning/ {
        proxy_pass http://learning_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 前端路由
    location / {
        proxy_pass http://student-frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://admin-frontend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /parent/ {
        proxy_pass http://parent-frontend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /teacher/ {
        proxy_pass http://teacher-frontend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. 測試計劃

### 5.1 服務啟動測試
1. 驗證所有容器正常啟動
2. 檢查服務健康狀態
3. 驗證網路連接

### 5.2 功能測試
1. **US-001 會員系統:** 註冊、登入、登出
2. **US-002 智慧出題:** 選擇條件、生成題目
3. **US-003 自動批改:** 提交答案、獲得結果
4. **US-005 學習歷程:** 記錄和查詢
5. **US-007 家長監控:** 查看學習狀況
6. **US-009 教師管理:** 班級管理功能

### 5.3 整合測試
1. 前後端 API 對接
2. 資料庫資料完整性
3. 跨服務通訊
4. 錯誤處理機制

---

## 6. 風險評估

### 6.1 技術風險
- **中等風險:** 服務依賴關係複雜
- **低風險:** 資料庫初始化失敗
- **低風險:** 前端 API 對接問題

### 6.2 緩解策略
1. 分階段啟動服務
2. 添加詳細的錯誤日誌
3. 準備回滾方案
4. 建立監控機制

---

## 7. 後續開發建議

### 7.1 短期目標 (1-2週)
1. 完成核心功能整合
2. 修復已知問題
3. 建立基本測試

### 7.2 中期目標 (1個月)
1. 添加 AI 分析服務
2. 完善通知系統
3. 優化性能

### 7.3 長期目標 (3個月)
1. 添加 Milvus/RAG 功能
2. 完善所有服務
3. 生產環境部署

---

## 8. 結論

當前架構基本完整，但需要進行以下關鍵修正：

1. **簡化 Docker Compose 配置** - 註釋不需要的服務
2. **添加缺失的前端服務** - 確保所有角色都能訪問
3. **整合章節資料** - 使用靜態 JSON 資料
4. **完善資料庫初始化** - 確保題庫資料正確載入
5. **驗證 API 整合** - 確保前後端通訊正常

修正完成後，系統將能夠支持 US-001、US-002、US-003、US-005、US-007、US-009 的完整功能測試。

**建議執行順序:**
1. 先修正 Docker Compose 配置
2. 再修正前端整合
3. 最後進行完整測試

---

**報告狀態:** 待確認  
**下一步:** 等待確認後開始執行修正 