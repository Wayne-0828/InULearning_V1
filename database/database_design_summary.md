# InULearning 學習練習記錄系統 - 資料庫設計總結

## 📊 階段一：資料庫設計完善 - 完成報告

### 🎯 設計目標
- ✅ 支援知識點追蹤系統
- ✅ 與登入用戶（PostgreSQL users 表）完整關聯  
- ✅ 符合現有專案設計架構
- ✅ 支援完整的練習記錄和歷程查看

### 🗄️ 資料庫表結構設計

#### 1. **升級現有表**

##### `learning_sessions` 表（學習會話）
```sql
-- 主要變更：新增完整的會話追蹤欄位
ALTER TABLE learning_sessions 
ADD COLUMN publisher VARCHAR(20) NOT NULL DEFAULT '南一',
ADD COLUMN difficulty VARCHAR(20),
ADD COLUMN correct_count INTEGER DEFAULT 0,
ADD COLUMN total_score DECIMAL(5,2),
ADD COLUMN accuracy_rate DECIMAL(5,2),
ADD COLUMN time_spent INTEGER,
ADD COLUMN session_metadata JSONB,
ADD COLUMN start_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN end_time TIMESTAMP WITH TIME ZONE;
```

**關鍵欄位**：
- `user_id INTEGER` → 關聯 `users(id)`
- `knowledge_points TEXT[]` → 知識點陣列追蹤
- `publisher` → 版本（南一/翰林/康軒）
- `accuracy_rate` → 正確率統計

##### `exercise_records` 表（練習記錄）
```sql
-- 主要變更：新增詳細的題目和答案資訊
ALTER TABLE exercise_records 
ADD COLUMN knowledge_points TEXT[],
ADD COLUMN question_content TEXT,
ADD COLUMN answer_choices JSONB,
ADD COLUMN difficulty VARCHAR(20),
ADD COLUMN score DECIMAL(5,2),
ADD COLUMN question_topic VARCHAR(200);
```

**關鍵欄位**：
- `user_id INTEGER` → 關聯 `users(id)`
- `knowledge_points TEXT[]` → 本題涉及的知識點
- `question_content TEXT` → 完整題目內容
- `answer_choices JSONB` → 選項內容

#### 2. **新增專用表**

##### `user_learning_profiles` 表（用戶學習檔案）
```sql
CREATE TABLE user_learning_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    current_grade VARCHAR(20),
    strength_knowledge_points TEXT[], -- 🔥 強項知識點
    weakness_knowledge_points TEXT[],  -- 🔥 弱項知識點
    total_practice_time INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    overall_accuracy DECIMAL(5,2) DEFAULT 0,
    preferred_difficulty VARCHAR(20) DEFAULT 'normal',
    learning_preferences JSONB
);
```

##### `knowledge_points_master` 表（知識點主表）
```sql
CREATE TABLE knowledge_points_master (
    id SERIAL PRIMARY KEY,
    knowledge_point VARCHAR(100) UNIQUE NOT NULL,
    subject VARCHAR(50) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    chapter VARCHAR(100),
    difficulty_level VARCHAR(20) DEFAULT 'normal',
    description TEXT,
    prerequisites TEXT[] -- 前置知識點
);
```

### 🎯 知識點追蹤系統

#### 知識點數據範例
```sql
-- 數學 8A 知識點
('一元一次方程式', '數學', '8A', '第1章 一元一次方程式', 'normal'),
('移項運算', '數學', '8A', '第1章 一元一次方程式', 'easy'),
('分數方程式', '數學', '8A', '第1章 一元一次方程式', 'hard'),
('應用問題', '數學', '8A', '第1章 一元一次方程式', 'hard'),

-- 英文 7A 知識點
('現在簡單式', '英文', '7A', '第1課 介紹自己', 'normal'),
('人稱代名詞', '英文', '7A', '第1課 介紹自己', 'easy'),
('be動詞', '英文', '7A', '第1課 介紹自己', 'easy'),
```

#### 知識點關聯方式
- **練習記錄中**: `exercise_records.knowledge_points[]` 記錄每題涉及的知識點
- **用戶檔案中**: `user_learning_profiles.strength/weakness_knowledge_points[]` 追蹤個人強弱項
- **會話中**: `learning_sessions.knowledge_points[]` 記錄本次練習涉及的所有知識點

### 🔗 用戶關聯設計

#### PostgreSQL 用戶關聯
所有核心表都與 `users(id)` 建立外鍵關聯：

```sql
-- 學習會話
learning_sessions.user_id → users(id)

-- 練習記錄  
exercise_records.user_id → users(id)

-- 用戶學習檔案
user_learning_profiles.user_id → users(id)
```

#### 多用戶數據隔離
- 每個用戶的學習數據完全隔離
- 支援 WHERE user_id = ? 的高效查詢
- 索引優化確保查詢效能

### 📈 高效能索引設計

#### 主要索引
```sql
-- 用戶查詢優化
CREATE INDEX idx_learning_sessions_user_subject ON learning_sessions(user_id, subject);
CREATE INDEX idx_exercise_records_user_subject ON exercise_records(user_id, subject);

-- 知識點檢索優化（GIN 索引）
CREATE INDEX idx_learning_sessions_knowledge_points ON learning_sessions USING GIN (knowledge_points);
CREATE INDEX idx_exercise_records_knowledge_points ON exercise_records USING GIN (knowledge_points);

-- 時間範圍查詢優化
CREATE INDEX idx_learning_sessions_created_at ON learning_sessions(created_at);
CREATE INDEX idx_exercise_records_created_at ON exercise_records(created_at);
```

### 🛡️ 數據完整性保證

#### 約束檢查
```sql
-- 年級約束
CONSTRAINT chk_grade CHECK (grade IN ('7A', '7B', '8A', '8B', '9A', '9B'))

-- 科目約束  
CONSTRAINT chk_subject CHECK (subject IN ('國文', '英文', '數學', '自然', '地理', '歷史', '公民'))

-- 版本約束
CONSTRAINT chk_publisher CHECK (publisher IN ('南一', '翰林', '康軒'))

-- 難度約束
CONSTRAINT chk_difficulty CHECK (difficulty IN ('easy', 'normal', 'hard'))
```

### 📋 完成的檔案

1. **`database_migration_learning_system.sql`** - 完整的資料庫升級腳本
2. **`init-scripts/init-postgres.sql`** - 更新的資料庫初始化腳本
3. **`database_design_summary.md`** - 本設計總結文檔

### ✅ 驗證清單

- [x] **知識點追蹤**: 完整的知識點系統，支援強弱項追蹤
- [x] **用戶關聯**: 所有表都與 users(id) 正確關聯
- [x] **現有兼容**: 保持與現有系統的完全兼容性
- [x] **效能優化**: 高效能索引設計，支援快速查詢
- [x] **數據完整性**: 完整的約束檢查和觸發器
- [x] **測試數據**: 包含完整的知識點測試數據

### 🚀 下一階段準備

資料庫結構已完全就緒，支援：
1. 練習結果的完整儲存（包含知識點）
2. 歷史記錄的高效查詢和篩選
3. 用戶學習檔案的動態更新
4. 知識點掌握程度的統計分析

**階段一完成！** 等待確認後開始階段二的後端API開發。