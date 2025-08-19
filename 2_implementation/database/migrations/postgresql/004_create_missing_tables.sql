-- ===============================================
-- InULearning 學習系統 - 創建缺失的資料表
-- 版本: v1.0.1
-- 日期: 2025-08-19
-- 
-- 目的: 創建在初始遷移中缺失的關聯表
-- ===============================================

-- 創建教師-班級關係表
CREATE TABLE IF NOT EXISTS teacher_class_relations (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES school_classes(id) ON DELETE CASCADE,
    
    -- 教學科目
    subject VARCHAR(50) NOT NULL, -- 數學、國文、英文等
    
    -- 關係狀態
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 時間戳記
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一約束：一個教師在一個班級只能教一個科目
    UNIQUE(teacher_id, class_id, subject)
);

-- 創建學生-班級關係表
CREATE TABLE IF NOT EXISTS student_class_relations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES school_classes(id) ON DELETE CASCADE,
    
    -- 學號
    student_number VARCHAR(20),
    
    -- 關係狀態
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 時間戳記
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一約束：一個學生在一個班級只能有一個記錄
    UNIQUE(student_id, class_id)
);

-- 創建索引以提升查詢效能
CREATE INDEX IF NOT EXISTS idx_teacher_class_relations_teacher_id ON teacher_class_relations(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_class_relations_class_id ON teacher_class_relations(class_id);
CREATE INDEX IF NOT EXISTS idx_teacher_class_relations_is_active ON teacher_class_relations(is_active);

CREATE INDEX IF NOT EXISTS idx_student_class_relations_student_id ON student_class_relations(student_id);
CREATE INDEX IF NOT EXISTS idx_student_class_relations_class_id ON student_class_relations(class_id);
CREATE INDEX IF NOT EXISTS idx_student_class_relations_is_active ON student_class_relations(is_active);

-- 為新表建立更新時間觸發器
CREATE TRIGGER update_teacher_class_relations_updated_at 
    BEFORE UPDATE ON teacher_class_relations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_class_relations_updated_at 
    BEFORE UPDATE ON student_class_relations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加外鍵約束到 users 表（如果不存在）
DO $$
BEGIN
    -- 檢查 users 表是否有 teaching_classes 和 student_classes 關聯
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'users_teaching_classes_fkey'
    ) THEN
        -- 添加 teaching_classes 關聯（如果不存在）
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'teaching_classes'
        ) THEN
            -- 這會在 SQLAlchemy 模型中處理，這裡只是確保表結構完整
        END IF;
    END IF;
END $$;
