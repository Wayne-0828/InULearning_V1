# 資料庫設計文檔 (Database Design Document) - InULearning 個人化學習平台

---

**文件版本 (Document Version):** `v1.0.0`

**最後更新 (Last Updated):** `2024-12-19`

**主要作者 (Lead Author):** `AIPE01_group2 Database Team`

**審核者 (Reviewers):** `系統架構師、後端團隊、DBA`

**狀態 (Status):** `草稿 (Draft)`

**相關文檔 (Related Documents):**
*   系統架構文檔: `../architecture/02_system_architecture_document.md`
*   系統設計文檔: `../detailed_design/03_system_design_document.md`
*   API 設計規範: `../api_design/04_api_design.md`

---

## 目錄 (Table of Contents)

1. [概述 (Overview)](#1-概述-overview)
2. [資料庫架構策略 (Database Architecture Strategy)](#2-資料庫架構策略-database-architecture-strategy)
3. [PostgreSQL 設計 (PostgreSQL Design)](#3-postgresql-設計-postgresql-design)
4. [MongoDB 設計 (MongoDB Design)](#4-mongodb-設計-mongodb-design)
5. [Redis 設計 (Redis Design)](#5-redis-設計-redis-design)
6. [資料同步與一致性 (Data Synchronization & Consistency)](#6-資料同步與一致性-data-synchronization--consistency)
7. [效能優化策略 (Performance Optimization)](#7-效能優化策略-performance-optimization)
8. [備份與災難恢復 (Backup & Disaster Recovery)](#8-備份與災難恢復-backup--disaster-recovery)
9. [安全性設計 (Security Design)](#9-安全性設計-security-design)
10. [監控與維護 (Monitoring & Maintenance)](#10-監控與維護-monitoring--maintenance)

---

## 1. 概述 (Overview)

### 1.1 設計原則 (Design Principles)

**多資料庫策略 (Polyglot Persistence):**
*   **PostgreSQL:** 結構化資料、事務處理、關聯查詢
*   **MongoDB:** 文檔資料、題庫內容、非結構化資料
*   **Redis:** 快取、會話管理、即時資料

**核心原則:**
*   **資料一致性:** 確保跨資料庫的資料同步與一致性
*   **效能優化:** 針對不同資料特性選擇最適合的儲存方式
*   **可擴展性:** 支援水平與垂直擴展
*   **高可用性:** 99.9% 以上的系統可用性
*   **安全性:** 資料加密、存取控制、審計日誌

### 1.2 資料分類 (Data Classification)

| 資料類型 | 特性 | 儲存方式 | 主要用途 |
|----------|------|----------|----------|
| **用戶資料** | 結構化、關聯性強 | PostgreSQL | 認證、檔案、權限 |
| **學習記錄** | 結構化、事務性 | PostgreSQL | 學習歷程、進度追蹤 |
| **題庫內容** | 半結構化、文檔型 | MongoDB | 題目、章節、知識點 |
| **AI 分析結果** | 非結構化、向量 | MongoDB | 弱點分析、推薦 |
| **會話資料** | 暫存、高頻存取 | Redis | 登入狀態、快取 |
| **即時統計** | 計數器、排行榜 | Redis | 即時統計、排名 |

---

## 2. 資料庫架構策略 (Database Architecture Strategy)

### 2.1 整體架構圖 (Overall Architecture)

```mermaid
graph TB
    subgraph "應用層 (Application Layer)"
        A1[Auth Service]
        A2[Learning Service]
        A3[Question Bank Service]
        A4[AI Analysis Service]
    end
    
    subgraph "資料存取層 (Data Access Layer)"
        B1[PostgreSQL Pool]
        B2[MongoDB Pool]
        B3[Redis Pool]
    end
    
    subgraph "資料庫層 (Database Layer)"
        C1[(PostgreSQL<br/>主要資料庫)]
        C2[(MongoDB<br/>題庫與內容)]
        C3[(Redis<br/>快取與會話)]
    end
    
    subgraph "基礎設施層 (Infrastructure Layer)"
        D1[Docker Containers]
        D2[Volume Mounts]
        D3[Network Bridge]
    end
    
    A1 --> B1
    A2 --> B1
    A2 --> B2
    A3 --> B2
    A4 --> B2
    A1 --> B3
    A2 --> B3
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    
    C1 --> D1
    C2 --> D1
    C3 --> D1
```

### 2.2 服務資料庫映射 (Service-Database Mapping)

| 微服務 | PostgreSQL | MongoDB | Redis | 主要資料類型 |
|--------|------------|---------|-------|-------------|
| **auth-service** | ✅ 主要 | ❌ | ✅ 會話 | 用戶認證、檔案 |
| **learning-service** | ✅ 主要 | ✅ 查詢 | ✅ 快取 | 學習記錄、進度 |
| **question-bank-service** | ❌ | ✅ 主要 | ✅ 快取 | 題庫、章節 |
| **ai-analysis-service** | ✅ 查詢 | ✅ 主要 | ✅ 快取 | AI 分析結果 |

---

## 3. PostgreSQL 設計 (PostgreSQL Design)

### 3.1 資料庫架構 (Database Schema)

#### **3.1.1 用戶管理 (User Management)**

**users 表 (主要用戶資料)**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_username_check CHECK (LENGTH(username) >= 3)
);

-- 索引設計
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**user_profiles 表 (用戶檔案)**
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    grade INTEGER CHECK (grade BETWEEN 7 AND 9),
    school VARCHAR(200),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    preferences JSONB,
    timezone VARCHAR(50) DEFAULT 'Asia/Taipei',
    language VARCHAR(10) DEFAULT 'zh-TW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_profile UNIQUE(user_id)
);

-- 索引設計
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_grade ON user_profiles(grade);
CREATE INDEX idx_user_profiles_school ON user_profiles(school);
```

#### **3.1.2 學習管理 (Learning Management)**

**learning_sessions 表 (學習會話)**
```sql
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    chapter VARCHAR(200),
    difficulty VARCHAR(20),
    question_count INTEGER NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    overall_score DECIMAL(5,2),
    time_spent INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_learning_sessions_grade CHECK (grade IN ('7A','7B','8A','8B','9A','9B')),
    CONSTRAINT chk_learning_sessions_subject CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民')),
    CONSTRAINT chk_learning_sessions_publisher CHECK (publisher IN ('南一','翰林','康軒')),
    CONSTRAINT chk_learning_sessions_difficulty CHECK (difficulty IN ('easy','normal','hard')),
    CONSTRAINT chk_learning_sessions_status CHECK (status IN ('active','completed','abandoned'))
);

-- 索引設計
CREATE INDEX idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_grade_subject ON learning_sessions(grade, subject);
CREATE INDEX idx_learning_sessions_status ON learning_sessions(status);
CREATE INDEX idx_learning_sessions_start_time ON learning_sessions(start_time);
```

**learning_records 表 (答題記錄)**
```sql
CREATE TABLE learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL, -- MongoDB ObjectId
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    chapter VARCHAR(200) NOT NULL,
    topic VARCHAR(200),
    knowledge_points TEXT[], -- 知識點陣列
    difficulty VARCHAR(20) NOT NULL,
    user_answer TEXT,
    correct_answer VARCHAR(5) NOT NULL, -- A/B/C/D
    is_correct BOOLEAN,
    score DECIMAL(5,2),
    time_spent INTEGER, -- 秒數
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_learning_records_grade CHECK (grade IN ('7A','7B','8A','8B','9A','9B')),
    CONSTRAINT chk_learning_records_subject CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民')),
    CONSTRAINT chk_learning_records_publisher CHECK (publisher IN ('南一','翰林','康軒')),
    CONSTRAINT chk_learning_records_difficulty CHECK (difficulty IN ('easy','normal','hard')),
    CONSTRAINT chk_learning_records_correct_answer CHECK (correct_answer IN ('A','B','C','D')),
    CONSTRAINT chk_learning_records_time_spent CHECK (time_spent IS NULL OR time_spent >= 0)
);

-- 索引設計
CREATE INDEX idx_learning_records_session_id ON learning_records(session_id);
CREATE INDEX idx_learning_records_question_id ON learning_records(question_id);
CREATE INDEX idx_learning_records_grade_subject ON learning_records(grade, subject, publisher);
CREATE INDEX idx_learning_records_is_correct ON learning_records(is_correct);
CREATE INDEX idx_learning_records_knowledge_points ON learning_records USING GIN(knowledge_points);
```

#### **3.1.3 用戶學習檔案 (User Learning Profiles)**

**user_learning_profiles 表 (用戶學習檔案)**
```sql
CREATE TABLE user_learning_profiles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    current_level INTEGER NOT NULL DEFAULT 1,
    strength_areas TEXT[],
    weakness_areas TEXT[],
    preferred_difficulty VARCHAR(20),
    learning_preferences JSONB,
    total_practice_time INTEGER NOT NULL DEFAULT 0,
    total_questions_answered INTEGER NOT NULL DEFAULT 0,
    average_accuracy DECIMAL(5,2),
    last_practice_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (user_id, grade, subject, publisher),
    CONSTRAINT chk_user_profiles_grade CHECK (grade IN ('7A','7B','8A','8B','9A','9B')),
    CONSTRAINT chk_user_profiles_subject CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民')),
    CONSTRAINT chk_user_profiles_publisher CHECK (publisher IN ('南一','翰林','康軒')),
    CONSTRAINT chk_user_profiles_difficulty CHECK (preferred_difficulty IN ('easy','normal','hard')),
    CONSTRAINT chk_user_profiles_level CHECK (current_level BETWEEN 1 AND 10)
);

-- 索引設計
CREATE INDEX idx_user_learning_profiles_composite ON user_learning_profiles(user_id, grade, subject);
```

#### **3.1.4 弱點分析歷史 (Weakness Analysis History)**

**weakness_analysis_history 表 (弱點分析歷史)**
```sql
CREATE TABLE weakness_analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    weak_concepts TEXT[] NOT NULL,
    knowledge_points_to_strengthen TEXT[] NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    accuracy_rate DECIMAL(5,2) NOT NULL,
    improvement_suggestions JSONB,
    trend_analysis JSONB,
    recommendations JSONB NOT NULL,
    analysis_version VARCHAR(10) NOT NULL DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_weakness_grade CHECK (grade IN ('7A','7B','8A','8B','9A','9B')),
    CONSTRAINT chk_weakness_subject CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民')),
    CONSTRAINT chk_weakness_publisher CHECK (publisher IN ('南一','翰林','康軒')),
    CONSTRAINT chk_weakness_overall_score CHECK (overall_score >= 0 AND overall_score <= 100),
    CONSTRAINT chk_weakness_accuracy_rate CHECK (accuracy_rate >= 0 AND accuracy_rate <= 100)
);

-- 索引設計
CREATE INDEX idx_weakness_analysis_user_subject ON weakness_analysis_history(user_id, subject, created_at);
CREATE INDEX idx_weakness_analysis_session ON weakness_analysis_history(session_id);
CREATE INDEX idx_weakness_analysis_concepts ON weakness_analysis_history USING GIN(weak_concepts);
CREATE INDEX idx_weakness_analysis_knowledge_points ON weakness_analysis_history USING GIN(knowledge_points_to_strengthen);
```

#### **3.1.5 學習進度快照 (Learning Progress Snapshots)**

**learning_progress_snapshots 表 (學習進度快照)**
```sql
CREATE TABLE learning_progress_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    snapshot_date DATE NOT NULL,
    total_sessions INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    average_score DECIMAL(5,2),
    accuracy_trend DECIMAL(5,2),
    mastered_concepts TEXT[],
    struggling_concepts TEXT[],
    difficulty_distribution JSONB,
    learning_velocity DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id, grade, subject, publisher, snapshot_date),
    CONSTRAINT chk_snapshots_grade CHECK (grade IN ('7A','7B','8A','8B','9A','9B')),
    CONSTRAINT chk_snapshots_subject CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民')),
    CONSTRAINT chk_snapshots_publisher CHECK (publisher IN ('南一','翰林','康軒')),
    CONSTRAINT chk_snapshots_score_range CHECK (average_score IS NULL OR (average_score >= 0 AND average_score <= 100)),
    CONSTRAINT chk_snapshots_accuracy_range CHECK (accuracy_trend IS NULL OR (accuracy_trend >= 0 AND accuracy_trend <= 100))
);

-- 索引設計
CREATE INDEX idx_progress_snapshots_user_date ON learning_progress_snapshots(user_id, subject, snapshot_date);
CREATE INDEX idx_progress_snapshots_trends ON learning_progress_snapshots(user_id, grade, subject, snapshot_date);
CREATE INDEX idx_progress_snapshots_concepts ON learning_progress_snapshots USING GIN(mastered_concepts);
CREATE INDEX idx_progress_snapshots_struggling ON learning_progress_snapshots USING GIN(struggling_concepts);
```

### 3.2 實體關係圖 (Entity-Relationship Diagram)

```mermaid
erDiagram
    USERS ||--o{ LEARNING_SESSIONS : starts
    USERS ||--o{ USER_LEARNING_PROFILES : has
    USERS ||--o{ WEAKNESS_ANALYSIS_HISTORY : analyzes
    USERS ||--o{ LEARNING_PROGRESS_SNAPSHOTS : tracks
    LEARNING_SESSIONS ||--o{ LEARNING_RECORDS : contains
    LEARNING_SESSIONS ||--o{ WEAKNESS_ANALYSIS_HISTORY : generates
    
    USERS {
        uuid id PK
        string username
        string email
        string password_hash
        enum role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    LEARNING_SESSIONS {
        uuid id PK
        uuid user_id FK
        string session_type
        string grade
        string subject
        string publisher
        string chapter
        string difficulty
        integer question_count
        timestamp start_time
        timestamp end_time
        string status
        decimal overall_score
        integer time_spent
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    LEARNING_RECORDS {
        uuid id PK
        uuid session_id FK
        string question_id
        string grade
        string subject
        string publisher
        string chapter
        string topic
        text-array knowledge_points
        string difficulty
        text user_answer
        string correct_answer
        boolean is_correct
        decimal score
        integer time_spent
        timestamp created_at
    }
    
    USER_LEARNING_PROFILES {
        uuid user_id PK,FK
        string grade PK
        string subject PK
        string publisher PK
        integer current_level
        text-array strength_areas
        text-array weakness_areas
        string preferred_difficulty
        jsonb learning_preferences
        integer total_practice_time
        integer total_questions_answered
        decimal average_accuracy
        date last_practice_date
        timestamp created_at
        timestamp updated_at
    }
    
    WEAKNESS_ANALYSIS_HISTORY {
        uuid id PK
        uuid session_id FK
        uuid user_id FK
        string grade
        string subject
        string publisher
        text-array weak_concepts
        text-array knowledge_points_to_strengthen
        decimal overall_score
        decimal accuracy_rate
        jsonb improvement_suggestions
        jsonb trend_analysis
        jsonb recommendations
        string analysis_version
        timestamp created_at
    }
    
    LEARNING_PROGRESS_SNAPSHOTS {
        uuid id PK
        uuid user_id FK
        string grade
        string subject
        string publisher
        date snapshot_date
        integer total_sessions
        integer total_questions
        decimal average_score
        decimal accuracy_trend
        text-array mastered_concepts
        text-array struggling_concepts
        jsonb difficulty_distribution
        decimal learning_velocity
        timestamp created_at
    }
```

### 3.3 資料類型與約束 (Data Types & Constraints)

#### **自定義類型 (Custom Types)**
```sql
-- 用戶角色枚舉
CREATE TYPE user_role_enum AS ENUM ('student', 'parent', 'teacher', 'admin');

-- 年級枚舉
CREATE TYPE grade_enum AS ENUM ('7A', '7B', '8A', '8B', '9A', '9B');

-- 科目枚舉
CREATE TYPE subject_enum AS ENUM ('國文', '英文', '數學', '自然', '地理', '歷史', '公民');

-- 出版商枚舉
CREATE TYPE publisher_enum AS ENUM ('南一', '翰林', '康軒');

-- 難度等級枚舉
CREATE TYPE difficulty_enum AS ENUM ('easy', 'normal', 'hard');

-- 會話狀態枚舉
CREATE TYPE session_status_enum AS ENUM ('active', 'completed', 'abandoned');
```

#### **觸發器與函數 (Triggers & Functions)**
```sql
-- 自動更新 updated_at 欄位
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 應用到相關表格
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_sessions_updated_at BEFORE UPDATE ON learning_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_learning_profiles_updated_at BEFORE UPDATE ON user_learning_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 4. MongoDB 設計 (MongoDB Design)

### 4.1 集合設計 (Collection Design)

#### **4.1.1 題庫集合 (Questions Collection)**

**questions 集合結構:**
```javascript
{
  _id: ObjectId("..."),
  id: "Q001-M7-001", // 唯一識別碼
  subject: "mathematics", // 科目
  grade: 7, // 年級
  chapter: "linear_equations", // 章節
  knowledge_points: ["solving_equations", "substitution_method"], // 知識點
  difficulty: "medium", // 難度
  question_type: "multiple_choice", // 題型
  content: {
    text: "解一元一次方程式：3x + 5 = 14",
    images: [], // 圖片URL陣列
    latex: "3x + 5 = 14" // LaTeX格式
  },
  options: [
    { id: "A", text: "x = 3", is_correct: true },
    { id: "B", text: "x = 4", is_correct: false },
    { id: "C", text: "x = 5", is_correct: false },
    { id: "D", text: "x = 6", is_correct: false }
  ],
  explanation: {
    text: "將方程式移項得到 3x = 14 - 5 = 9，因此 x = 3",
    steps: [
      "3x + 5 = 14",
      "3x = 14 - 5",
      "3x = 9",
      "x = 3"
    ]
  },
  metadata: {
    source: "textbook_chapter_3", // 來源
    author: "teacher_wang", // 作者
    reviewed: true, // 是否已審核
    tags: ["algebra", "basic"], // 標籤
    estimated_time: 120, // 預估作答時間(秒)
    usage_count: 0, // 使用次數
    correct_rate: 0.85 // 正確率
  },
  created_at: ISODate("2024-12-19T00:00:00Z"),
  updated_at: ISODate("2024-12-19T00:00:00Z")
}
```

**索引設計:**
```javascript
// 複合索引 - 查詢效能優化
db.questions.createIndex({ 
  "subject": 1, 
  "grade": 1, 
  "difficulty": 1,
  "metadata.reviewed": 1 
});

// 知識點索引 - 支援陣列查詢
db.questions.createIndex({ "knowledge_points": 1 });

// 章節索引
db.questions.createIndex({ "chapter": 1 });

// 全文搜索索引
db.questions.createIndex({ 
  "content.text": "text",
  "explanation.text": "text"
});

// 唯一識別碼索引
db.questions.createIndex({ "id": 1 }, { unique: true });
```

#### **4.1.2 章節集合 (Chapters Collection)**

**chapters 集合結構:**
```javascript
{
  _id: ObjectId("..."),
  id: "CH-M7-001",
  subject: "mathematics",
  grade: 7,
  name: "一元一次方程式",
  description: "學習一元一次方程式的解法與應用",
  order: 1, // 章節順序
  knowledge_points: [
    {
      id: "KP-001",
      name: "方程式基本概念",
      description: "理解方程式的定義與基本性質",
      order: 1
    },
    {
      id: "KP-002", 
      name: "移項法則",
      description: "掌握移項的技巧與規則",
      order: 2
    }
  ],
  prerequisites: ["CH-M7-000"], // 先修章節
  difficulty_distribution: {
    easy: 30,
    medium: 50,
    hard: 20
  },
  estimated_hours: 8, // 預估學習時數
  metadata: {
    curriculum_standard: "108課綱",
    publisher: "翰林出版社",
    version: "2024版"
  },
  created_at: ISODate("2024-12-19T00:00:00Z"),
  updated_at: ISODate("2024-12-19T00:00:00Z")
}
```

#### **4.1.3 AI分析結果集合 (AI Analysis Collection)**

**weakness_analysis 集合結構:**
```javascript
{
  _id: ObjectId("..."),
  user_id: "550e8400-e29b-41d4-a716-446655440000", // PostgreSQL UUID
  session_id: "550e8400-e29b-41d4-a716-446655440001",
  analysis_type: "weakness_analysis",
  subject: "mathematics",
  analysis_result: {
    overall_score: 75.5,
    weak_areas: [
      {
        knowledge_point: "solving_equations",
        mastery_level: 0.65,
        error_patterns: ["calculation_errors", "sign_errors"],
        recommendation: "需要加強基本運算練習"
      },
      {
        knowledge_point: "word_problems",
        mastery_level: 0.45,
        error_patterns: ["reading_comprehension", "equation_setup"],
        recommendation: "需要增加應用題解題步驟練習"
      }
    ],
    strengths: [
      {
        knowledge_point: "basic_operations",
        mastery_level: 0.95,
        note: "基本運算能力良好"
      }
    ],
    learning_suggestions: [
      {
        type: "practice",
        content: "建議進行20題方程式基本運算練習",
        priority: "high"
      },
      {
        type: "review",
        content: "複習正負號運算規則",
        priority: "medium"
      }
    ]
  },
  generated_by: "gemini-1.5-pro",
  confidence_score: 0.87,
  created_at: ISODate("2024-12-19T00:00:00Z")
}
```

### 4.2 資料驗證 (Data Validation)

**MongoDB Schema 驗證規則:**
```javascript
// questions 集合驗證規則
db.createCollection("questions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "subject", "grade", "content", "difficulty"],
      properties: {
        id: {
          bsonType: "string",
          pattern: "^[A-Z0-9-]+$"
        },
        subject: {
          bsonType: "string",
          enum: ["mathematics", "chinese", "english", "science", "social"]
        },
        grade: {
          bsonType: "int",
          minimum: 7,
          maximum: 9
        },
        difficulty: {
          bsonType: "string",
          enum: ["easy", "medium", "hard", "expert"]
        },
        question_type: {
          bsonType: "string",
          enum: ["multiple_choice", "true_false", "fill_blank", "essay"]
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
```

---

## 5. Redis 設計 (Redis Design)

### 5.1 資料結構設計 (Data Structure Design)

#### **5.1.1 會話管理 (Session Management)**

**會話儲存格式:**
```redis
# 用戶會話資料
SET "session:550e8400-e29b-41d4-a716-446655440000" "{
  \"user_id\": \"550e8400-e29b-41d4-a716-446655440000\",
  \"username\": \"student_chen\",
  \"role\": \"student\",
  \"last_activity\": \"2024-12-19T10:30:00Z\",
  \"ip_address\": \"192.168.1.100\",
  \"user_agent\": \"Mozilla/5.0...\"
}" EX 3600

# JWT Token 黑名單
SET "blacklist:token:abc123..." "revoked" EX 86400

# 登入嘗試計數器
INCR "login_attempts:user_chen@example.com" EX 300
```

#### **5.1.2 學習狀態快取 (Learning State Cache)**

**學習進度快取:**
```redis
# 用戶當前學習會話
SET "learning:current_session:550e8400-e29b-41d4-a716-446655440000" "{
  \"session_id\": \"550e8400-e29b-41d4-a716-446655440001\",
  \"current_question\": 5,
  \"total_questions\": 10,
  \"start_time\": \"2024-12-19T10:00:00Z\",
  \"answers\": [...]
}" EX 7200

# 用戶答題統計快取
HSET "stats:user:550e8400-e29b-41d4-a716-446655440000" 
  "total_questions" 1250
  "correct_answers" 987
  "accuracy_rate" 0.789
  "last_updated" "2024-12-19T10:30:00Z"

# 設定過期時間
EXPIRE "stats:user:550e8400-e29b-41d4-a716-446655440000" 1800
```

#### **5.1.3 即時排行榜 (Real-time Leaderboards)**

**排行榜設計:**
```redis
# 週排行榜 (使用 Sorted Set)
ZADD "leaderboard:weekly:2024-W51" 
  987 "user:550e8400-e29b-41d4-a716-446655440000"
  1023 "user:550e8400-e29b-41d4-a716-446655440001"
  856 "user:550e8400-e29b-41d4-a716-446655440002"

# 取得前10名
ZREVRANGE "leaderboard:weekly:2024-W51" 0 9 WITHSCORES

# 年級別排行榜
ZADD "leaderboard:grade7:monthly:2024-12" 
  987 "user:550e8400-e29b-41d4-a716-446655440000"

# 科目別排行榜
ZADD "leaderboard:mathematics:weekly:2024-W51"
  95.5 "user:550e8400-e29b-41d4-a716-446655440000"
```

#### **5.1.4 系統快取 (System Cache)**

**API 回應快取:**
```redis
# 題庫查詢結果快取
SET "cache:questions:mathematics:grade7:medium" "{
  \"total\": 150,
  \"questions\": [...],
  \"cached_at\": \"2024-12-19T10:30:00Z\"
}" EX 300

# 用戶檔案快取
SET "cache:profile:550e8400-e29b-41d4-a716-446655440000" "{
  \"display_name\": \"陳小明\",
  \"grade\": 7,
  \"school\": \"明德國中\",
  \"preferences\": {...}
}" EX 1800

# 章節資料快取
SET "cache:chapters:mathematics:grade7" "[...]" EX 3600
```

### 5.2 命名規範與過期策略 (Naming Convention & Expiration Strategy)

#### **命名規範:**
*   **會話:** `session:{user_id}` (1小時過期)
*   **快取:** `cache:{type}:{key}` (5-60分鐘過期)
*   **統計:** `stats:{type}:{id}` (30分鐘過期)
*   **排行榜:** `leaderboard:{scope}:{period}` (依週期更新)
*   **計數器:** `counter:{type}:{id}` (依需求過期)

#### **過期策略:**
| 資料類型 | 過期時間 | 更新策略 |
|----------|----------|----------|
| 用戶會話 | 1小時 | 活動時延長 |
| API快取 | 5-15分鐘 | 主動失效 |
| 用戶統計 | 30分鐘 | 定期更新 |
| 排行榜 | 1天 | 定時重建 |
| 計數器 | 5分鐘 | 依需求重設 |

---

## 6. 資料同步與一致性 (Data Synchronization & Consistency)

### 6.1 跨資料庫一致性策略 (Cross-Database Consistency Strategy)

#### **6.1.1 最終一致性 (Eventual Consistency)**

**學習記錄同步流程:**
```mermaid
sequenceDiagram
    participant App as 應用服務
    participant PG as PostgreSQL
    participant Mongo as MongoDB
    participant Redis as Redis
    
    App->>PG: 1. 寫入學習記錄
    PG-->>App: 2. 確認寫入
    App->>Redis: 3. 更新統計快取
    App->>Mongo: 4. 非同步更新AI分析
    
    Note over App: 如果步驟4失敗，使用重試機制
    
    App->>Redis: 5. 清除相關快取
    Redis-->>App: 6. 確認清除
```

#### **6.1.2 資料同步機制 (Data Synchronization Mechanism)**

**同步策略:**
*   **即時同步:** 關鍵業務資料 (用戶認證、學習記錄)
*   **非同步同步:** 分析結果、統計資料
*   **批次同步:** 歷史資料歸檔、報表生成

**實作方式:**
```python
# 示例：學習記錄同步服務
class LearningRecordSyncService:
    def save_learning_record(self, record_data):
        try:
            # 1. 主要資料庫寫入 (PostgreSQL)
            pg_record = self.pg_repo.create_learning_record(record_data)
            
            # 2. 更新快取 (Redis)
            self.redis_service.update_user_stats(record_data['user_id'])
            
            # 3. 非同步更新分析資料 (MongoDB)
            self.message_queue.send({
                'type': 'update_analysis',
                'record_id': pg_record.id,
                'data': record_data
            })
            
            return pg_record
            
        except Exception as e:
            # 回滾機制
            self.handle_sync_failure(record_data, e)
            raise
```

### 6.2 衝突解決策略 (Conflict Resolution Strategy)

#### **6.2.1 衝突檢測 (Conflict Detection)**
*   **時間戳比較:** 使用 `updated_at` 欄位比較
*   **版本控制:** 樂觀鎖定機制
*   **校驗和檢查:** 資料完整性驗證

#### **6.2.2 衝突解決規則 (Conflict Resolution Rules)**
*   **最後寫入勝出 (Last Write Wins):** 適用於用戶偏好設定
*   **合併策略 (Merge Strategy):** 適用於學習統計資料
*   **手動介入 (Manual Intervention):** 適用於關鍵業務資料

---

## 7. 效能優化策略 (Performance Optimization)

### 7.1 查詢優化 (Query Optimization)

#### **7.1.1 PostgreSQL 優化**

**索引策略:**
```sql
-- 複合索引 - 支援多條件查詢
CREATE INDEX idx_learning_sessions_user_subject_status 
ON learning_sessions(user_id, subject, status)
WHERE status = 'active';

-- 部分索引 - 只索引活躍資料
CREATE INDEX idx_active_users ON users(id, email) 
WHERE is_active = true;

-- 表達式索引 - 支援函數查詢
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

**查詢優化範例:**
```sql
-- 優化前 - 效能較差
SELECT * FROM learning_records 
WHERE session_id IN (
    SELECT id FROM learning_sessions 
    WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
);

-- 優化後 - 使用 JOIN
SELECT lr.* FROM learning_records lr
INNER JOIN learning_sessions ls ON lr.session_id = ls.id
WHERE ls.user_id = '550e8400-e29b-41d4-a716-446655440000';
```

#### **7.1.2 MongoDB 優化**

**聚合管線優化:**
```javascript
// 題目查詢聚合管線
db.questions.aggregate([
  // 1. 篩選條件盡早執行
  { $match: { 
    subject: "mathematics", 
    grade: 7, 
    "metadata.reviewed": true 
  }},
  
  // 2. 投影減少資料傳輸
  { $project: {
    id: 1,
    content: 1,
    options: 1,
    difficulty: 1,
    knowledge_points: 1
  }},
  
  // 3. 隨機抽樣
  { $sample: { size: 10 }},
  
  // 4. 排序
  { $sort: { difficulty: 1 }}
]);
```

### 7.2 連接池配置 (Connection Pool Configuration)

#### **7.2.1 PostgreSQL 連接池**
```python
# SQLAlchemy 連接池配置
DATABASE_CONFIG = {
    'pool_size': 20,           # 基本連接數
    'max_overflow': 30,        # 最大溢位連接數
    'pool_timeout': 30,        # 連接超時時間
    'pool_recycle': 3600,      # 連接回收時間
    'pool_pre_ping': True,     # 連接前ping檢查
}
```

#### **7.2.2 MongoDB 連接池**
```python
# PyMongo 連接池配置
MONGODB_CONFIG = {
    'maxPoolSize': 50,         # 最大連接數
    'minPoolSize': 5,          # 最小連接數
    'maxIdleTimeMS': 30000,    # 最大空閒時間
    'serverSelectionTimeoutMS': 5000,  # 伺服器選擇超時
}
```

### 7.3 快取策略 (Caching Strategy)

#### **7.3.1 多層快取架構**
```mermaid
graph TD
    A[應用請求] --> B[應用層快取]
    B --> C{命中?}
    C -->|是| D[返回資料]
    C -->|否| E[Redis快取]
    E --> F{命中?}
    F -->|是| G[更新應用層快取]
    F -->|否| H[資料庫查詢]
    H --> I[更新Redis快取]
    G --> D
    I --> G
```

#### **7.3.2 快取更新策略**
*   **Cache-Aside:** 應用程式管理快取
*   **Write-Through:** 同步寫入資料庫和快取
*   **Write-Behind:** 非同步寫入資料庫

---

## 8. 備份與災難恢復 (Backup & Disaster Recovery)

### 8.1 備份策略 (Backup Strategy)

#### **8.1.1 PostgreSQL 備份**
```bash
#!/bin/bash
# 每日完整備份腳本
pg_dump -h localhost -U postgres -d inulearning \
  --format=custom \
  --compress=9 \
  --file="/backup/postgres/inulearning_$(date +%Y%m%d).dump"

# 每小時增量備份 (使用 WAL)
pg_basebackup -D /backup/postgres/wal_backup \
  -Ft -z -P -h localhost -U postgres
```

#### **8.1.2 MongoDB 備份**
```bash
#!/bin/bash
# MongoDB 備份腳本
mongodump --host localhost:27017 \
  --db inulearning_content \
  --gzip \
  --out /backup/mongodb/$(date +%Y%m%d)

# 使用 mongodump 進行集合級別備份
mongodump --host localhost:27017 \
  --db inulearning_content \
  --collection questions \
  --gzip \
  --out /backup/mongodb/questions_$(date +%Y%m%d)
```

#### **8.1.3 Redis 備份**
```bash
#!/bin/bash
# Redis 備份腳本
redis-cli --rdb /backup/redis/dump_$(date +%Y%m%d_%H%M).rdb

# AOF 備份
redis-cli BGREWRITEAOF
cp /var/lib/redis/appendonly.aof /backup/redis/aof_$(date +%Y%m%d_%H%M).aof
```

### 8.2 災難恢復計劃 (Disaster Recovery Plan)

#### **8.2.1 恢復時間目標 (RTO/RPO)**
| 資料庫 | RTO (恢復時間) | RPO (資料遺失) | 備份頻率 |
|--------|----------------|----------------|----------|
| PostgreSQL | < 30分鐘 | < 1小時 | 每小時 |
| MongoDB | < 15分鐘 | < 4小時 | 每4小時 |
| Redis | < 5分鐘 | < 15分鐘 | 每15分鐘 |

#### **8.2.2 恢復程序 (Recovery Procedures)**
```bash
# PostgreSQL 恢復
pg_restore -h localhost -U postgres -d inulearning_recovery \
  /backup/postgres/inulearning_20241219.dump

# MongoDB 恢復
mongorestore --host localhost:27017 \
  --db inulearning_content_recovery \
  --gzip /backup/mongodb/20241219/inulearning_content

# Redis 恢復
redis-cli FLUSHALL
redis-cli --rdb /backup/redis/dump_20241219_1030.rdb
```

---

## 9. 安全性設計 (Security Design)

### 9.1 存取控制 (Access Control)

#### **9.1.1 資料庫用戶權限**
```sql
-- PostgreSQL 權限設計
-- 應用程式專用用戶
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE inulearning TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 唯讀分析用戶
CREATE USER analytics_user WITH PASSWORD 'analytics_password';
GRANT CONNECT ON DATABASE inulearning TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;

-- 備份專用用戶
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE inulearning TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

#### **9.1.2 MongoDB 權限設計**
```javascript
// 建立應用程式用戶
db.createUser({
  user: "app_user",
  pwd: "secure_password",
  roles: [
    { role: "readWrite", db: "inulearning_content" }
  ]
});

// 建立唯讀分析用戶
db.createUser({
  user: "analytics_user", 
  pwd: "analytics_password",
  roles: [
    { role: "read", db: "inulearning_content" }
  ]
});
```

### 9.2 資料加密 (Data Encryption)

#### **9.2.1 傳輸加密**
*   **PostgreSQL:** SSL/TLS 連接
*   **MongoDB:** TLS 加密連接
*   **Redis:** AUTH 認證 + TLS

#### **9.2.2 靜態資料加密**
```sql
-- PostgreSQL 敏感欄位加密
-- 使用 pgcrypto 擴展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密用戶個人資料
CREATE TABLE user_sensitive_data (
    user_id UUID PRIMARY KEY,
    encrypted_phone bytea, -- 加密後的電話
    encrypted_id_number bytea, -- 加密後的身分證字號
    encryption_key_id VARCHAR(50) -- 加密金鑰ID
);
```

### 9.3 審計日誌 (Audit Logging)

#### **9.3.1 資料庫操作日誌**
```sql
-- PostgreSQL 審計日誌表
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    user_id UUID,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- 審計觸發器範例
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, new_values)
        VALUES (TG_TABLE_NAME, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, old_values, new_values)
        VALUES (TG_TABLE_NAME, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, old_values)
        VALUES (TG_TABLE_NAME, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 10. 監控與維護 (Monitoring & Maintenance)

### 10.1 效能監控 (Performance Monitoring)

#### **10.1.1 關鍵指標 (Key Metrics)**

**PostgreSQL 監控指標:**
*   連接數使用率
*   查詢執行時間
*   緩存命中率
*   死鎖次數
*   表格和索引大小

**MongoDB 監控指標:**
*   集合查詢效能
*   索引使用率
*   記憶體使用量
*   複寫延遲
*   分片平衡狀態

**Redis 監控指標:**
*   記憶體使用率
*   命中率
*   連接數
*   過期鍵清理
*   持久化狀態

#### **10.1.2 監控工具配置**
```yaml
# Prometheus + Grafana 監控配置
version: '3.8'
services:
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://monitor_user:password@postgres:5432/inulearning?sslmode=disable"
    
  mongodb-exporter:
    image: percona/mongodb_exporter
    command: 
      - '--mongodb.uri=mongodb://monitor_user:password@mongodb:27017'
    
  redis-exporter:
    image: oliver006/redis_exporter
    environment:
      REDIS_ADDR: "redis:6379"
```

### 10.2 維護計劃 (Maintenance Plan)

#### **10.2.1 定期維護任務**

**每日維護 (Daily Maintenance):**
```bash
#!/bin/bash
# 每日維護腳本

# PostgreSQL 統計資料更新
psql -d inulearning -c "ANALYZE;"

# MongoDB 索引重建檢查
mongo inulearning_content --eval "db.runCommand({reIndex: 'questions'})"

# Redis 記憶體清理
redis-cli MEMORY PURGE

# 備份驗證
./verify_backups.sh
```

**每週維護 (Weekly Maintenance):**
```bash
#!/bin/bash
# 每週維護腳本

# PostgreSQL VACUUM 作業
psql -d inulearning -c "VACUUM ANALYZE;"

# 索引使用情況分析
psql -d inulearning -f analyze_index_usage.sql

# 慢查詢日誌分析
./analyze_slow_queries.sh

# 容量使用情況報告
./generate_capacity_report.sh
```

#### **10.2.2 自動化維護**
```python
# 自動化維護腳本範例
class DatabaseMaintenanceService:
    def __init__(self):
        self.pg_conn = self.get_pg_connection()
        self.mongo_client = self.get_mongo_client()
        self.redis_client = self.get_redis_client()
    
    def daily_maintenance(self):
        """每日維護任務"""
        try:
            # PostgreSQL 統計更新
            self.update_pg_statistics()
            
            # MongoDB 索引檢查
            self.check_mongodb_indexes()
            
            # Redis 記憶體清理
            self.cleanup_redis_memory()
            
            # 生成維護報告
            self.generate_maintenance_report()
            
        except Exception as e:
            self.send_alert(f"Daily maintenance failed: {e}")
    
    def weekly_maintenance(self):
        """每週維護任務"""
        try:
            # 深度分析
            self.analyze_query_performance()
            
            # 容量規劃
            self.capacity_planning()
            
            # 安全性檢查
            self.security_audit()
            
        except Exception as e:
            self.send_alert(f"Weekly maintenance failed: {e}")
```

---

## 11. 資料庫遷移腳本 (Database Migration Scripts)

### 11.1 PostgreSQL 遷移腳本

```sql
-- 創建學習會話表
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    chapter VARCHAR(200),
    difficulty VARCHAR(20),
    question_count INTEGER NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    overall_score DECIMAL(5,2),
    time_spent INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 創建學習記錄表
CREATE TABLE learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id),
    question_id VARCHAR(100) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    chapter VARCHAR(200) NOT NULL,
    topic VARCHAR(200),
    knowledge_points TEXT[],
    difficulty VARCHAR(20) NOT NULL,
    user_answer TEXT,
    correct_answer VARCHAR(5) NOT NULL,
    is_correct BOOLEAN,
    score DECIMAL(5,2),
    time_spent INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 創建用戶學習檔案表
CREATE TABLE user_learning_profiles (
    user_id UUID NOT NULL REFERENCES users(id),
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    current_level INTEGER NOT NULL DEFAULT 1,
    strength_areas TEXT[],
    weakness_areas TEXT[],
    preferred_difficulty VARCHAR(20),
    learning_preferences JSONB,
    total_practice_time INTEGER NOT NULL DEFAULT 0,
    total_questions_answered INTEGER NOT NULL DEFAULT 0,
    average_accuracy DECIMAL(5,2),
    last_practice_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, grade, subject, publisher)
);

-- 創建弱點分析歷史記錄表
CREATE TABLE weakness_analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id),
    user_id UUID NOT NULL REFERENCES users(id),
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    weak_concepts TEXT[] NOT NULL,
    knowledge_points_to_strengthen TEXT[] NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    accuracy_rate DECIMAL(5,2) NOT NULL,
    improvement_suggestions JSONB,
    trend_analysis JSONB,
    recommendations JSONB NOT NULL,
    analysis_version VARCHAR(10) NOT NULL DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 創建學習進度快照表
CREATE TABLE learning_progress_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(20) NOT NULL,
    snapshot_date DATE NOT NULL,
    total_sessions INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    average_score DECIMAL(5,2),
    accuracy_trend DECIMAL(5,2),
    mastered_concepts TEXT[],
    struggling_concepts TEXT[],
    difficulty_distribution JSONB,
    learning_velocity DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, grade, subject, publisher, snapshot_date)
);

-- 建立索引
CREATE INDEX idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_grade_subject ON learning_sessions(grade, subject);
CREATE INDEX idx_learning_sessions_status ON learning_sessions(status);

CREATE INDEX idx_learning_records_session_id ON learning_records(session_id);
CREATE INDEX idx_learning_records_grade_subject ON learning_records(grade, subject, publisher);
CREATE INDEX idx_learning_records_knowledge_points ON learning_records USING GIN (knowledge_points);

CREATE INDEX idx_user_learning_profiles_composite ON user_learning_profiles(user_id, grade, subject);

CREATE INDEX idx_weakness_analysis_user_subject ON weakness_analysis_history(user_id, subject, created_at);
CREATE INDEX idx_weakness_analysis_session ON weakness_analysis_history(session_id);
CREATE INDEX idx_weakness_analysis_concepts ON weakness_analysis_history USING GIN (weak_concepts);
CREATE INDEX idx_weakness_analysis_knowledge_points ON weakness_analysis_history USING GIN (knowledge_points_to_strengthen);

CREATE INDEX idx_progress_snapshots_user_date ON learning_progress_snapshots(user_id, subject, snapshot_date);
CREATE INDEX idx_progress_snapshots_trends ON learning_progress_snapshots(user_id, grade, subject, snapshot_date);
CREATE INDEX idx_progress_snapshots_concepts ON learning_progress_snapshots USING GIN (mastered_concepts);
CREATE INDEX idx_progress_snapshots_struggling ON learning_progress_snapshots USING GIN (struggling_concepts);

-- 添加約束檢查
ALTER TABLE learning_sessions ADD CONSTRAINT chk_grade 
    CHECK (grade IN ('7A','7B','8A','8B','9A','9B'));
    
ALTER TABLE learning_sessions ADD CONSTRAINT chk_subject 
    CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民'));
    
ALTER TABLE learning_sessions ADD CONSTRAINT chk_publisher 
    CHECK (publisher IN ('南一','翰林','康軒'));
    
ALTER TABLE learning_sessions ADD CONSTRAINT chk_difficulty 
    CHECK (difficulty IN ('easy','normal','hard'));

-- 為弱點分析歷史表添加約束
ALTER TABLE weakness_analysis_history ADD CONSTRAINT chk_weakness_grade 
    CHECK (grade IN ('7A','7B','8A','8B','9A','9B'));
    
ALTER TABLE weakness_analysis_history ADD CONSTRAINT chk_weakness_subject 
    CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民'));
    
ALTER TABLE weakness_analysis_history ADD CONSTRAINT chk_weakness_publisher 
    CHECK (publisher IN ('南一','翰林','康軒'));

ALTER TABLE weakness_analysis_history ADD CONSTRAINT chk_overall_score_range 
    CHECK (overall_score >= 0 AND overall_score <= 100);

ALTER TABLE weakness_analysis_history ADD CONSTRAINT chk_accuracy_rate_range 
    CHECK (accuracy_rate >= 0 AND accuracy_rate <= 100);

-- 為學習進度快照表添加約束
ALTER TABLE learning_progress_snapshots ADD CONSTRAINT chk_snapshots_grade 
    CHECK (grade IN ('7A','7B','8A','8B','9A','9B'));
    
ALTER TABLE learning_progress_snapshots ADD CONSTRAINT chk_snapshots_subject 
    CHECK (subject IN ('國文','英文','數學','自然','地理','歷史','公民'));
    
ALTER TABLE learning_progress_snapshots ADD CONSTRAINT chk_snapshots_publisher 
    CHECK (publisher IN ('南一','翰林','康軒'));

ALTER TABLE learning_progress_snapshots ADD CONSTRAINT chk_snapshots_score_range 
    CHECK (average_score IS NULL OR (average_score >= 0 AND average_score <= 100));

ALTER TABLE learning_progress_snapshots ADD CONSTRAINT chk_snapshots_accuracy_range 
    CHECK (accuracy_trend IS NULL OR (accuracy_trend >= 0 AND accuracy_trend <= 100));
```

---

**文件審核記錄 (Review History):**

| 日期 | 審核人 | 版本 | 變更摘要/主要反饋 |
| :--------- | :--------- | :--- | :---------------------------------------------- |
| 2024-12-19 | AIPE01_group2 Database Team | v1.0.0 | 資料庫設計文檔初版，涵蓋PostgreSQL、MongoDB、Redis完整設計架構與優化策略 |
| 2024-12-19 | AIPE01_group2 Database Team | v1.1.0 | 根據系統設計文檔修正資料庫設計，完善學習相關表格結構，新增弱點分析和進度快照功能 | 