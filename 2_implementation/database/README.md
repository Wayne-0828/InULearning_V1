# InULearning 資料庫管理

## 📁 目錄結構

```
2_implementation/database/
├── migrations/           # 資料庫遷移檔案
│   ├── postgresql/      # PostgreSQL 遷移腳本
│   │   └── 001_init_learning_system.sql
│   └── mongodb/         # MongoDB 遷移腳本 (預留)
├── seeds/               # 種子數據檔案
│   └── postgresql/      # PostgreSQL 種子數據
│       └── knowledge_points_seed.sql
├── scripts/             # 資料庫管理腳本
│   └── setup_database.sh
└── README.md           # 本文檔
```

## 🚀 快速開始

### 1. 自動化設置（推薦）

```bash
# 執行自動化設置腳本
./2_implementation/database/scripts/setup_database.sh
```

### 2. 手動設置

```bash
# 1. 執行 PostgreSQL 遷移
psql -h localhost -U aipe-tester -d inulearning -f 2_implementation/database/migrations/postgresql/001_init_learning_system.sql

# 2. 插入知識點種子數據
psql -h localhost -U aipe-tester -d inulearning -f 2_implementation/database/seeds/postgresql/knowledge_points_seed.sql
```

## 🗄️ 資料庫結構

### 核心表格

| 表名 | 用途 | 關鍵欄位 |
|------|------|----------|
| `users` | 用戶管理 | `id`, `username`, `email`, `role` |
| `learning_sessions` | 學習會話 | `user_id`, `subject`, `knowledge_points[]` |
| `exercise_records` | 練習記錄 | `session_id`, `user_id`, `knowledge_points[]` |
| `user_learning_profiles` | 用戶學習檔案 | `user_id`, `strength_knowledge_points[]`, `weakness_knowledge_points[]` |
| `knowledge_points_master` | 知識點主表 | `knowledge_point`, `subject`, `grade`, `difficulty_level` |

### 關鍵特色

#### 🎯 知識點追蹤系統
- **多層級追蹤**: 題目 → 會話 → 用戶檔案
- **強弱項分析**: 自動識別用戶強項和弱項知識點
- **前置依賴**: 支援知識點間的前置關係

#### 🔗 用戶關聯設計
- **完整關聯**: 所有核心表都與 `users(id)` 建立外鍵
- **數據隔離**: 每個用戶的學習數據完全隔離
- **角色支援**: 支援學生、家長、教師、管理員角色

#### 📈 高效能索引
- **GIN 索引**: 針對知識點陣列的高效檢索
- **複合索引**: 用戶+科目的組合查詢優化
- **時間索引**: 支援日期範圍的歷史記錄查詢

## 📊 知識點系統

### 知識點分類

```sql
-- 查看所有科目的知識點統計
SELECT 
    subject,
    grade,
    COUNT(*) as knowledge_point_count,
    COUNT(CASE WHEN difficulty_level = 'easy' THEN 1 END) as easy_count,
    COUNT(CASE WHEN difficulty_level = 'normal' THEN 1 END) as normal_count,
    COUNT(CASE WHEN difficulty_level = 'hard' THEN 1 END) as hard_count
FROM knowledge_points_master 
GROUP BY subject, grade 
ORDER BY subject, grade;
```

### 用戶知識點掌握分析

```sql
-- 查看用戶的知識點掌握情況
SELECT 
    er.user_id,
    UNNEST(er.knowledge_points) as knowledge_point,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END) as correct_attempts,
    ROUND(
        (SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
        2
    ) as mastery_rate
FROM exercise_records er
WHERE er.user_id = ? AND er.knowledge_points IS NOT NULL
GROUP BY er.user_id, UNNEST(er.knowledge_points)
HAVING COUNT(*) >= 3
ORDER BY mastery_rate ASC;
```

## 🔧 常用查詢

### 學習歷程查詢

```sql
-- 查詢用戶的學習歷程（支援篩選）
SELECT 
    ls.id,
    ls.session_name,
    ls.subject,
    ls.grade,
    ls.publisher,
    ls.chapter,
    ls.question_count,
    ls.correct_count,
    ls.accuracy_rate,
    ls.time_spent,
    ls.knowledge_points,
    ls.created_at
FROM learning_sessions ls
WHERE ls.user_id = ?
    AND ls.subject = COALESCE(?, ls.subject)
    AND ls.grade = COALESCE(?, ls.grade)
    AND ls.created_at BETWEEN COALESCE(?, '1900-01-01') AND COALESCE(?, '2100-12-31')
ORDER BY ls.created_at DESC
LIMIT ? OFFSET ?;
```

### 統計查詢

```sql
-- 用戶學習統計
SELECT 
    COUNT(DISTINCT ls.id) as total_sessions,
    SUM(ls.question_count) as total_questions,
    SUM(ls.correct_count) as total_correct,
    ROUND(AVG(ls.accuracy_rate), 2) as avg_accuracy,
    SUM(ls.time_spent) as total_time_spent
FROM learning_sessions ls
WHERE ls.user_id = ?
    AND ls.status = 'completed'
    AND ls.created_at >= ?;
```

## 🛠️ 維護操作

### 重建索引

```sql
-- 重建知識點相關的 GIN 索引
REINDEX INDEX idx_learning_sessions_knowledge_points;
REINDEX INDEX idx_exercise_records_knowledge_points;
REINDEX INDEX idx_user_profiles_strength_knowledge;
REINDEX INDEX idx_user_profiles_weakness_knowledge;
```

### 清理測試數據

```sql
-- 清理測試用戶的數據（謹慎使用）
DELETE FROM exercise_records WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%');
DELETE FROM learning_sessions WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%');
DELETE FROM user_learning_profiles WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%');
DELETE FROM users WHERE username LIKE 'test_%';
```

### 備份和恢復

```bash
# 備份資料庫
pg_dump -h localhost -U aipe-tester -d inulearning > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢復資料庫
psql -h localhost -U aipe-tester -d inulearning < backup_20241219_120000.sql
```

## 📈 效能監控

### 查詢效能分析

```sql
-- 查看慢查詢（需要開啟 log_statement_stats）
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE query LIKE '%learning_sessions%' OR query LIKE '%exercise_records%'
ORDER BY mean_time DESC
LIMIT 10;
```

### 索引使用情況

```sql
-- 查看索引使用統計
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename IN ('learning_sessions', 'exercise_records', 'user_learning_profiles')
ORDER BY idx_tup_read DESC;
```

## 🔄 版本管理

### 遷移檔案命名規則

```
{序號}_{描述}.sql
例如: 001_init_learning_system.sql
```

### 新增遷移

1. 在 `migrations/postgresql/` 目錄下創建新的 SQL 檔案
2. 使用遞增的序號命名
3. 在檔案開頭添加註解說明變更內容
4. 執行遷移腳本測試

### 種子數據更新

1. 修改 `seeds/postgresql/` 目錄下的相關檔案
2. 使用 `ON CONFLICT ... DO NOTHING` 避免重複插入
3. 重新執行種子數據腳本

## 🚨 注意事項

1. **生產環境**: 在生產環境執行遷移前，請先備份資料庫
2. **權限管理**: 確保應用程式用戶有適當的資料庫權限
3. **索引維護**: 定期檢查和重建索引以保持查詢效能
4. **數據清理**: 定期清理過期的測試數據和日誌
5. **監控告警**: 設置資料庫效能和空間使用的監控告警

## 📞 支援

如有資料庫相關問題，請聯繫開發團隊或查看相關文檔：
- 系統設計文檔: `1_system_design/database_design/`
- API 文檔: `1_system_design/api_design/`
- 故障排除指南: `3_testing/troubleshooting/`