# 開發規範與編碼標準 (Development Guidelines & Coding Standards) - InULearning 平台

---

**文件版本:** `v1.0.0`  
**最後更新:** `2024-12-19`  
**主要作者:** `AIPE01_group2 Tech Team`  
**狀態:** `Draft`

---

## 目錄

1. [總體開發原則](#1-總體開發原則)
2. [Python 後端編碼規範](#2-python-後端編碼規範)
3. [JavaScript 前端編碼規範](#3-javascript-前端編碼規範)
4. [資料庫設計規範](#4-資料庫設計規範)
5. [Git 版本控制規範](#5-git-版本控制規範)
6. [文檔撰寫規範](#6-文檔撰寫規範)
7. [測試規範](#7-測試規範)
8. [程式碼審查流程](#8-程式碼審查流程)

---

## 1. 總體開發原則

### 1.1 編碼原則
- **可讀性優先:** 程式碼應該清晰易讀，自我說明
- **DRY原則:** 避免重複程式碼
- **SOLID原則:** 遵循物件導向設計原則
- **效能考量:** 在可讀性與效能間取得平衡
- **安全第一:** 所有程式碼必須考慮資安風險

### 1.2 命名規範
- **描述性命名:** 變數、函數、類別名稱應清楚表達用途
- **一致性:** 相同專案內使用一致的命名風格
- **避免縮寫:** 除非是廣為人知的縮寫（如 `id`, `url`）

---

## 2. Python 後端編碼規範

### 2.1 程式碼格式化
- 使用 **Black** 進行自動格式化
- 行長度限制：**88字元**
- 縮排：**4個空格**
- 字串：優先使用**雙引號**

### 2.2 命名規範
```python
# 類別 - PascalCase
class UserService:
    pass

# 函數與變數 - snake_case
def get_user_profile(user_id: str) -> UserProfile:
    current_user = get_current_user()
    return current_user

# 常數 - UPPER_SNAKE_CASE
DATABASE_URL = "postgresql://..."
MAX_RETRY_COUNT = 3

# 私有屬性 - 前綴底線
class UserRepository:
    def __init__(self):
        self._connection = None
```

### 2.3 型別提示
```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# 必須使用型別提示
def calculate_score(
    answers: List[str], 
    correct_answers: List[str]
) -> Dict[str, Any]:
    pass

# Pydantic 模型
class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "student"
```

### 2.4 錯誤處理
```python
# 使用具體的例外類型
try:
    user = user_repository.get_by_id(user_id)
except UserNotFoundError as e:
    logger.error(f"User not found: {user_id}", exc_info=True)
    raise HTTPException(status_code=404, detail="User not found")

# 自定義例外類別
class InULearningError(Exception):
    """基礎例外類別"""
    pass

class UserNotFoundError(InULearningError):
    """用戶不存在例外"""
    pass
```

### 2.5 日誌記錄
```python
import logging

logger = logging.getLogger(__name__)

def process_learning_session(session_id: str):
    logger.info(f"Processing session: {session_id}")
    
    try:
        # 處理邏輯
        logger.debug(f"Session {session_id} processed successfully")
    except Exception as e:
        logger.error(f"Failed to process session {session_id}: {e}", exc_info=True)
        raise
```

---

## 3. JavaScript 前端編碼規範

### 3.1 程式碼格式化
- 使用 **Prettier** 進行自動格式化
- 縮排：**2個空格**
- 字串：優先使用**單引號**
- 語句結尾：**必須使用分號**

### 3.2 命名規範
```javascript
// 類別 - PascalCase
class UserProfile {
  constructor(userData) {
    this.userData = userData;
  }
}

// 函數與變數 - camelCase
const getCurrentUser = () => {
  const userToken = localStorage.getItem('token');
  return parseUserFromToken(userToken);
};

// 常數 - UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.inulearning.com';
const MAX_RETRY_ATTEMPTS = 3;

// DOM 元素 - $ 前綴
const $loginForm = document.getElementById('login-form');
const $submitButton = $loginForm.querySelector('.submit-btn');
```

### 3.3 函數定義
```javascript
// 優先使用箭頭函數
const calculateAccuracy = (correct, total) => {
  if (total === 0) return 0;
  return Math.round((correct / total) * 100);
};

// 複雜函數使用 JSDoc
/**
 * 提交學習會話答案
 * @param {string} sessionId - 會話ID
 * @param {Array<Object>} answers - 答案陣列
 * @param {Function} onSuccess - 成功回調
 * @param {Function} onError - 錯誤回調
 */
const submitAnswers = async (sessionId, answers, onSuccess, onError) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers })
    });
    
    if (response.ok) {
      const result = await response.json();
      onSuccess(result);
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    console.error('Submit failed:', error);
    onError(error);
  }
};
```

### 3.4 錯誤處理
```javascript
// 統一錯誤處理
class APIError extends Error {
  constructor(message, status, code) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
  }
}

// 全域錯誤處理
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  showErrorMessage('系統發生錯誤，請稍後再試');
});
```

---

## 4. 資料庫設計規範

### 4.1 PostgreSQL 規範
```sql
-- 表格命名：snake_case
CREATE TABLE learning_sessions (
    -- 主鍵：使用 UUID
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 欄位命名：snake_case
    user_id UUID NOT NULL,
    session_type VARCHAR(50) NOT NULL,
    
    -- 時間戳：統一使用 TIMESTAMP WITH TIME ZONE
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 外鍵約束：明確命名
    CONSTRAINT fk_learning_sessions_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 檢查約束：描述性命名
    CONSTRAINT chk_learning_sessions_score_positive 
        CHECK (score >= 0)
);

-- 索引命名：idx_表格_欄位
CREATE INDEX idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_status ON learning_sessions(status);
```

### 4.2 MongoDB 規範
```javascript
// 集合命名：複數形式，snake_case
// 文檔結構：camelCase
{
  _id: ObjectId("..."),
  questionId: "Q001-M7-001",
  subject: "mathematics",
  grade: 7,
  content: {
    text: "題目內容",
    images: [],
    metadata: {
      difficulty: "medium",
      estimatedTime: 120
    }
  },
  createdAt: ISODate("2024-12-19T00:00:00Z"),
  updatedAt: ISODate("2024-12-19T00:00:00Z")
}

// 索引命名規範
db.questions.createIndex(
  { "subject": 1, "grade": 1, "difficulty": 1 },
  { name: "idx_questions_subject_grade_difficulty" }
);
```

---

## 5. Git 版本控制規範

### 5.1 分支命名
```bash
# 主分支
main              # 正式環境
develop          # 開發環境

# 功能分支
feature/user-authentication
feature/learning-analytics
feature/question-bank

# 修復分支
hotfix/critical-security-fix
bugfix/session-timeout-issue

# 發布分支
release/v1.0.0
```

### 5.2 提交訊息格式
```bash
# 格式：<類型>(<範圍>): <描述>
# 
# <詳細說明>
# 
# <關聯議題>

feat(auth): 新增 JWT 認證功能

- 實作 JWT token 生成與驗證
- 新增 refresh token 機制
- 整合 Redis 會話管理

Closes #123

# 類型標籤：
feat     # 新功能
fix      # 錯誤修復
docs     # 文檔更新
style    # 格式調整
refactor # 重構
test     # 測試相關
chore    # 建置相關
```

### 5.3 Pull Request 規範
```markdown
## 📝 變更描述
簡要說明此次變更的內容與目的

## 🎯 變更類型
- [ ] 新功能 (feature)
- [ ] 錯誤修復 (bugfix)
- [ ] 重構 (refactor)
- [ ] 文檔更新 (docs)

## 🧪 測試
- [ ] 單元測試已通過
- [ ] 整合測試已通過
- [ ] 手動測試已完成

## 📋 檢查清單
- [ ] 程式碼符合編碼規範
- [ ] 已新增必要的測試
- [ ] 文檔已更新
- [ ] 無安全性問題

## 🔗 相關議題
Closes #123
```

---

## 6. 文檔撰寫規範

### 6.1 README 格式
```markdown
# 專案名稱

簡要描述專案功能與目的

## 🚀 快速開始

### 環境需求
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose

### 安裝步驟
1. 複製專案：`git clone ...`
2. 安裝依賴：`pip install -r requirements.txt`
3. 啟動服務：`docker-compose up -d`

## 📁 專案結構
```
project/
├── backend/          # 後端服務
├── frontend/         # 前端應用
├── docs/            # 文檔
└── tests/           # 測試
```

## 🛠️ 開發指南
- [API 文檔](./docs/api.md)
- [資料庫設計](./docs/database.md)
- [部署指南](./docs/deployment.md)
```

### 6.2 API 文檔格式
```markdown
## POST /api/auth/login

用戶登入認證

### 請求參數
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| email | string | Yes | 用戶信箱 |
| password | string | Yes | 密碼 |

### 請求範例
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 回應範例
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "user": {
    "id": "123",
    "email": "user@example.com",
    "role": "student"
  }
}
```

### 錯誤代碼
| 代碼 | 說明 |
|------|------|
| 400 | 請求參數錯誤 |
| 401 | 認證失敗 |
| 500 | 伺服器錯誤 |
```

---

## 7. 測試規範

### 7.1 單元測試（Python）
```python
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService

class TestUserService:
    def setup_method(self):
        self.user_service = UserService()
    
    def test_get_user_profile_success(self):
        # Arrange
        user_id = "test-user-id"
        expected_profile = {"id": user_id, "name": "Test User"}
        
        # Act
        with patch.object(self.user_service, 'repository') as mock_repo:
            mock_repo.get_by_id.return_value = expected_profile
            result = self.user_service.get_user_profile(user_id)
        
        # Assert
        assert result == expected_profile
        mock_repo.get_by_id.assert_called_once_with(user_id)
    
    def test_get_user_profile_not_found(self):
        # Arrange
        user_id = "non-existent-user"
        
        # Act & Assert
        with patch.object(self.user_service, 'repository') as mock_repo:
            mock_repo.get_by_id.side_effect = UserNotFoundError()
            
            with pytest.raises(UserNotFoundError):
                self.user_service.get_user_profile(user_id)
```

### 7.2 整合測試（JavaScript）
```javascript
describe('學習會話 API', () => {
  beforeEach(() => {
    // 測試設定
    localStorage.clear();
    fetchMock.reset();
  });

  test('提交答案成功', async () => {
    // Arrange
    const sessionId = 'test-session-id';
    const answers = [{ questionId: 'Q1', answer: 'A' }];
    const expectedResponse = { score: 85, correct: 8, total: 10 };
    
    fetchMock.post(`/api/sessions/${sessionId}/submit`, {
      status: 200,
      body: expectedResponse
    });

    // Act
    const result = await submitAnswers(sessionId, answers);

    // Assert
    expect(result).toEqual(expectedResponse);
    expect(fetchMock.called()).toBe(true);
  });

  test('提交答案失敗 - 網路錯誤', async () => {
    // Arrange
    const sessionId = 'test-session-id';
    const answers = [{ questionId: 'Q1', answer: 'A' }];
    
    fetchMock.post(`/api/sessions/${sessionId}/submit`, {
      status: 500,
      body: { error: 'Internal Server Error' }
    });

    // Act & Assert
    await expect(submitAnswers(sessionId, answers))
      .rejects.toThrow('HTTP 500');
  });
});
```

### 7.3 測試覆蓋率要求
- **單元測試:** ≥ 80%
- **整合測試:** ≥ 70%
- **E2E 測試:** 覆蓋主要用戶流程

---

## 8. 程式碼審查流程

### 8.1 審查檢查項目

#### **功能性檢查**
- [ ] 程式碼實作符合需求規格
- [ ] 邊界條件處理正確
- [ ] 錯誤處理完善
- [ ] 效能考量適當

#### **程式碼品質檢查**
- [ ] 命名規範一致
- [ ] 程式碼結構清晰
- [ ] 註解充足且準確
- [ ] 無重複程式碼

#### **安全性檢查**
- [ ] 輸入驗證完整
- [ ] 無 SQL 注入風險
- [ ] 敏感資料加密
- [ ] 權限控制正確

#### **測試檢查**
- [ ] 測試覆蓋率達標
- [ ] 測試案例完整
- [ ] 測試可以穩定執行
- [ ] 模擬資料合理

### 8.2 審查流程
1. **提交 PR:** 開發者建立 Pull Request
2. **自動檢查:** CI/CD 執行測試與程式碼分析
3. **同儕審查:** 至少一位同事進行程式碼審查
4. **修改調整:** 根據審查意見進行修改
5. **最終確認:** 審查者確認修改後批准合併
6. **合併主分支:** 自動部署至測試環境

### 8.3 審查意見範例
```markdown
## 🔍 審查意見

### ✅ 優點
- 程式碼結構清晰，易於理解
- 錯誤處理完善
- 測試覆蓋率良好

### 🔧 建議改進
1. **Line 45**: 建議將 magic number 定義為常數
   ```python
   # 建議改為
   MAX_RETRY_COUNT = 3
   if retry_count > MAX_RETRY_COUNT:
   ```

2. **Line 67**: 函數過於複雜，建議拆分為多個小函數

### ❌ 必須修正
1. **Line 23**: 缺少輸入驗證，可能導致安全風險
2. **Line 89**: 記憶體洩漏風險，需要適當釋放資源

### 📝 其他
- 建議新增 docstring 說明函數用途
- 考慮新增單元測試涵蓋邊界情況
```

---

**文件審核記錄:**

| 日期 | 審核人 | 版本 | 變更摘要 |
|------|--------|------|----------|
| 2024-12-19 | AIPE01_group2 Tech Team | v1.0.0 | 開發規範初版建立 | 