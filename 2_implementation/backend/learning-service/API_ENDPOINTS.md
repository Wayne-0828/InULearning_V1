# Learning Service API 端點文檔

## 新增的學習歷程 API 端點

### 1. 完成練習並提交結果

**端點**: `POST /api/v1/learning/exercises/complete`
**描述**: 學生完成練習後提交所有結果，系統自動創建學習會話和練習記錄

**請求體**:
```json
{
  "session_name": "數學練習 - 一元一次方程式",
  "subject": "數學",
  "grade": "8A",
  "chapter": "一元一次方程式",
  "publisher": "南一",
  "difficulty": "normal",
  "knowledge_points": ["一元一次方程式", "移項運算"],
  "exercise_results": [
    {
      "question_id": "q_123456",
      "subject": "數學",
      "grade": "8A",
      "chapter": "一元一次方程式",
      "publisher": "南一",
      "knowledge_points": ["一元一次方程式", "移項運算"],
      "question_content": "解方程式 2x + 3 = 7",
      "answer_choices": {"A": "x = 2", "B": "x = 3", "C": "x = 4", "D": "x = 5"},
      "difficulty": "normal",
      "question_topic": "一元一次方程式解法",
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "score": 100.0,
      "explanation": "移項得到 2x = 4，所以 x = 2",
      "time_spent": 45
    }
  ],
  "total_time_spent": 1800,
  "session_metadata": {"source": "web", "device": "desktop"}
}
```

**響應**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_questions": 10,
  "correct_count": 8,
  "total_score": 85.5,
  "accuracy_rate": 80.0,
  "time_spent": 1800,
  "created_at": "2024-12-19T10:00:00"
}
```

### 2. 查詢學習歷程記錄

**端點**: `GET /api/v1/learning/records`
**描述**: 查詢用戶的學習歷程記錄，支持多種篩選條件

**查詢參數**:
- `subject` (optional): 科目篩選
- `grade` (optional): 年級篩選
- `publisher` (optional): 出版社篩選
- `start_date` (optional): 開始日期
- `end_date` (optional): 結束日期
- `page` (default: 1): 頁碼
- `page_size` (default: 20): 每頁數量

**響應**:
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "session_name": "數學練習 - 一元一次方程式",
      "subject": "數學",
      "grade": "8A",
      "chapter": "一元一次方程式",
      "publisher": "南一",
      "difficulty": "normal",
      "knowledge_points": ["一元一次方程式", "移項運算"],
      "question_count": 10,
      "correct_count": 8,
      "total_score": 85.5,
      "accuracy_rate": 80.0,
      "time_spent": 1800,
      "status": "completed",
      "start_time": "2024-12-19T10:00:00",
      "end_time": "2024-12-19T10:30:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 3. 查詢會話詳細資訊

**端點**: `GET /api/v1/learning/records/{session_id}`
**描述**: 查詢特定會話的詳細資訊，包括所有練習記錄

**響應**:
```json
{
  "session": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_name": "數學練習 - 一元一次方程式",
    "subject": "數學",
    "grade": "8A",
    "chapter": "一元一次方程式",
    "publisher": "南一",
    "difficulty": "normal",
    "knowledge_points": ["一元一次方程式", "移項運算"],
    "question_count": 10,
    "correct_count": 8,
    "total_score": 85.5,
    "accuracy_rate": 80.0,
    "time_spent": 1800,
    "status": "completed",
    "start_time": "2024-12-19T10:00:00",
    "end_time": "2024-12-19T10:30:00"
  },
  "exercise_records": [
    {
      "id": "record_123456",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 1,
      "question_id": "q_123456",
      "subject": "數學",
      "grade": "8A",
      "chapter": "一元一次方程式",
      "publisher": "南一",
      "knowledge_points": ["一元一次方程式", "移項運算"],
      "question_content": "解方程式 2x + 3 = 7",
      "answer_choices": {"A": "x = 2", "B": "x = 3", "C": "x = 4", "D": "x = 5"},
      "difficulty": "normal",
      "question_topic": "一元一次方程式解法",
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "score": 100.0,
      "explanation": "移項得到 2x = 4，所以 x = 2",
      "time_spent": 45,
      "created_at": "2024-12-19T10:15:00"
    }
  ]
}
```

### 4. 獲取學習統計資訊

**端點**: `GET /api/v1/learning/statistics`
**描述**: 獲取用戶的學習統計資訊

**響應**:
```json
{
  "total_sessions": 25,
  "total_questions": 250,
  "total_correct": 200,
  "overall_accuracy": 80.0,
  "total_time_spent": 45000,
  "subject_stats": {
    "數學": {"sessions": 10, "accuracy": 85.0, "avg_score": 87.5},
    "英文": {"sessions": 8, "accuracy": 75.0, "avg_score": 78.0}
  },
  "recent_performance": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "subject": "數學",
      "date": "2024-12-19T10:00:00",
      "score": 85.5,
      "accuracy": 80.0,
      "questions": 10
    }
  ]
}
```

## 兼容性端點

### 學生學習記錄查詢（兼容舊API）

**端點**: `GET /api/v1/learning/student/records`
**描述**: 學生查詢自己的學習記錄（重定向到新API）

**端點**: `GET /api/v1/learning/student/statistics`
**描述**: 學生查詢自己的學習統計（重定向到新API）

## 資料庫結構

### 主要表格

1. **learning_sessions**: 學習會話表
2. **exercise_records**: 練習記錄表
3. **user_learning_profiles**: 用戶學習檔案表
4. **knowledge_points_master**: 知識點主表

### 知識點追蹤

系統支援完整的知識點追蹤：
- 會話級別：`learning_sessions.knowledge_points`
- 題目級別：`exercise_records.knowledge_points`
- 用戶級別：`user_learning_profiles.strength_knowledge_points` 和 `weakness_knowledge_points`

### 統計功能

- 自動計算正確率、平均分數
- 按科目、年級、出版社分類統計
- 近期表現趨勢分析
- 知識點掌握度分析