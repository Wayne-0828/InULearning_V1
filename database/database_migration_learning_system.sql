-- ===============================================
-- InULearning 學習練習記錄系統資料庫升級腳本
-- 版本: v1.0.0
-- 作者: AIPE01_group2
-- 日期: 2024-12-19
-- 
-- 目的: 升級現有資料庫以支援完整的學習練習記錄功能
-- 包含知識點追蹤、詳細練習記錄、用戶學習檔案等
-- ===============================================

-- 確保UUID擴展存在
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===============================================
-- 1. 升級 learning_sessions 表
-- ===============================================

-- 檢查現有表結構並擴充
DO $$
BEGIN
    -- 添加缺少的欄位
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'publisher') THEN
        ALTER TABLE learning_sessions ADD COLUMN publisher VARCHAR(20);
        UPDATE learning_sessions SET publisher = '南一' WHERE publisher IS NULL;
        ALTER TABLE learning_sessions ALTER COLUMN publisher SET NOT NULL;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'difficulty') THEN
        ALTER TABLE learning_sessions ADD COLUMN difficulty VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'correct_count') THEN
        ALTER TABLE learning_sessions ADD COLUMN correct_count INTEGER DEFAULT 0;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'total_score') THEN
        ALTER TABLE learning_sessions ADD COLUMN total_score DECIMAL(5,2);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'accuracy_rate') THEN
        ALTER TABLE learning_sessions ADD COLUMN accuracy_rate DECIMAL(5,2);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'time_spent') THEN
        ALTER TABLE learning_sessions ADD COLUMN time_spent INTEGER; -- 秒數
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'session_metadata') THEN
        ALTER TABLE learning_sessions ADD COLUMN session_metadata JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'start_time') THEN
        ALTER TABLE learning_sessions ADD COLUMN start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'learning_sessions' AND column_name = 'end_time') THEN
        ALTER TABLE learning_sessions ADD COLUMN end_time TIMESTAMP WITH TIME ZONE;
    END IF;

    -- 修改 session_name 長度限制
    ALTER TABLE learning_sessions ALTER COLUMN session_name TYPE VARCHAR(200);
END $$;

-- 添加約束檢查
DO $$
BEGIN
    -- 檢查並添加 publisher 約束
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'chk_learning_sessions_publisher') THEN
        ALTER TABLE learning_sessions ADD CONSTRAINT chk_learning_sessions_publisher 
            CHECK (publisher IN ('南一', '翰林', '康軒'));
    END IF;

    -- 檢查並添加 difficulty 約束  
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'chk_learning_sessions_difficulty') THEN
        ALTER TABLE learning_sessions ADD CONSTRAINT chk_learning_sessions_difficulty 
            CHECK (difficulty IN ('easy', 'normal', 'hard') OR difficulty IS NULL);
    END IF;

    -- 檢查並添加 grade 約束
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'chk_learning_sessions_grade') THEN
        ALTER TABLE learning_sessions ADD CONSTRAINT chk_learning_sessions_grade 
            CHECK (grade IN ('7A', '7B', '8A', '8B', '9A', '9B'));
    END IF;

    -- 檢查並添加 subject 約束
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'chk_learning_sessions_subject') THEN
        ALTER TABLE learning_sessions ADD CONSTRAINT chk_learning_sessions_subject 
            CHECK (subject IN ('國文', '英文', '數學', '自然', '地理', '歷史', '公民'));
    END IF;
END $$;

-- ===============================================
-- 2. 升級 exercise_records 表
-- ===============================================

DO $$
BEGIN
    -- 添加練習記錄的詳細欄位
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'subject') THEN
        ALTER TABLE exercise_records ADD COLUMN subject VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'grade') THEN
        ALTER TABLE exercise_records ADD COLUMN grade VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'chapter') THEN
        ALTER TABLE exercise_records ADD COLUMN chapter VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'publisher') THEN
        ALTER TABLE exercise_records ADD COLUMN publisher VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'knowledge_points') THEN
        ALTER TABLE exercise_records ADD COLUMN knowledge_points TEXT[];
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'question_content') THEN
        ALTER TABLE exercise_records ADD COLUMN question_content TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'answer_choices') THEN
        ALTER TABLE exercise_records ADD COLUMN answer_choices JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'difficulty') THEN
        ALTER TABLE exercise_records ADD COLUMN difficulty VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'score') THEN
        ALTER TABLE exercise_records ADD COLUMN score DECIMAL(5,2);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'exercise_records' AND column_name = 'question_topic') THEN
        ALTER TABLE exercise_records ADD COLUMN question_topic VARCHAR(200);
    END IF;
END $$;

-- ===============================================
-- 3. 創建 user_learning_profiles 表
-- ===============================================

CREATE TABLE IF NOT EXISTS user_learning_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_grade VARCHAR(20),
    preferred_subjects TEXT[],
    preferred_publishers TEXT[],
    -- 知識點追蹤
    strength_knowledge_points TEXT[], -- 強項知識點
    weakness_knowledge_points TEXT[],  -- 弱項知識點
    -- 統計數據
    total_practice_time INTEGER DEFAULT 0, -- 總練習時間（秒）
    total_sessions INTEGER DEFAULT 0,      -- 總練習會話數
    total_questions INTEGER DEFAULT 0,     -- 總答題數
    correct_questions INTEGER DEFAULT 0,   -- 總答對數
    overall_accuracy DECIMAL(5,2) DEFAULT 0, -- 整體正確率
    -- 學習偏好
    preferred_difficulty VARCHAR(20) DEFAULT 'normal',
    learning_preferences JSONB,            -- 其他學習偏好設置
    -- 時間追蹤
    last_practice_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 約束檢查
    CONSTRAINT chk_user_profiles_grade 
        CHECK (current_grade IN ('7A', '7B', '8A', '8B', '9A', '9B') OR current_grade IS NULL),
    CONSTRAINT chk_user_profiles_difficulty 
        CHECK (preferred_difficulty IN ('easy', 'normal', 'hard')),
    CONSTRAINT chk_user_profiles_accuracy_range 
        CHECK (overall_accuracy >= 0 AND overall_accuracy <= 100)
);

-- ===============================================
-- 4. 創建 knowledge_points_master 表（知識點主表）
-- ===============================================

CREATE TABLE IF NOT EXISTS knowledge_points_master (
    id SERIAL PRIMARY KEY,
    knowledge_point VARCHAR(100) UNIQUE NOT NULL,
    subject VARCHAR(50) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    chapter VARCHAR(100),
    difficulty_level VARCHAR(20) DEFAULT 'normal',
    description TEXT,
    prerequisites TEXT[], -- 前置知識點
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 約束檢查
    CONSTRAINT chk_knowledge_points_subject 
        CHECK (subject IN ('國文', '英文', '數學', '自然', '地理', '歷史', '公民')),
    CONSTRAINT chk_knowledge_points_grade 
        CHECK (grade IN ('7A', '7B', '8A', '8B', '9A', '9B')),
    CONSTRAINT chk_knowledge_points_difficulty 
        CHECK (difficulty_level IN ('easy', 'normal', 'hard'))
);

-- ===============================================
-- 5. 創建 learning_analytics 表（學習分析）
-- ===============================================

CREATE TABLE IF NOT EXISTS learning_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    subject VARCHAR(50) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- 分析結果
    weak_knowledge_points TEXT[],      -- 本次發現的弱項知識點
    improved_knowledge_points TEXT[],  -- 本次有改善的知識點
    recommendations JSONB,             -- AI推薦建議
    
    -- 表現指標
    session_accuracy DECIMAL(5,2),     -- 本次練習正確率
    improvement_trend VARCHAR(20),      -- 改善趨勢 (improving/stable/declining)
    learning_velocity DECIMAL(5,2),    -- 學習速度指標
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 約束檢查
    CONSTRAINT chk_analytics_subject 
        CHECK (subject IN ('國文', '英文', '數學', '自然', '地理', '歷史', '公民')),
    CONSTRAINT chk_analytics_grade 
        CHECK (grade IN ('7A', '7B', '8A', '8B', '9A', '9B')),
    CONSTRAINT chk_analytics_accuracy_range 
        CHECK (session_accuracy >= 0 AND session_accuracy <= 100),
    CONSTRAINT chk_analytics_trend 
        CHECK (improvement_trend IN ('improving', 'stable', 'declining'))
);

-- ===============================================
-- 6. 創建索引以提升查詢效能
-- ===============================================

-- learning_sessions 索引
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_subject ON learning_sessions(user_id, subject);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_grade_subject_publisher ON learning_sessions(grade, subject, publisher);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_created_at ON learning_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_status ON learning_sessions(status);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_knowledge_points ON learning_sessions USING GIN (knowledge_points);

-- exercise_records 索引
CREATE INDEX IF NOT EXISTS idx_exercise_records_user_subject ON exercise_records(user_id, subject);
CREATE INDEX IF NOT EXISTS idx_exercise_records_knowledge_points ON exercise_records USING GIN (knowledge_points);
CREATE INDEX IF NOT EXISTS idx_exercise_records_is_correct ON exercise_records(is_correct);
CREATE INDEX IF NOT EXISTS idx_exercise_records_created_at ON exercise_records(created_at);

-- user_learning_profiles 索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_grade_subject ON user_learning_profiles(current_grade);
CREATE INDEX IF NOT EXISTS idx_user_profiles_strength_knowledge ON user_learning_profiles USING GIN (strength_knowledge_points);
CREATE INDEX IF NOT EXISTS idx_user_profiles_weakness_knowledge ON user_learning_profiles USING GIN (weakness_knowledge_points);

-- knowledge_points_master 索引
CREATE INDEX IF NOT EXISTS idx_knowledge_points_subject_grade ON knowledge_points_master(subject, grade);
CREATE INDEX IF NOT EXISTS idx_knowledge_points_chapter ON knowledge_points_master(chapter);

-- learning_analytics 索引
CREATE INDEX IF NOT EXISTS idx_analytics_user_date ON learning_analytics(user_id, analysis_date);
CREATE INDEX IF NOT EXISTS idx_analytics_subject_grade ON learning_analytics(subject, grade);
CREATE INDEX IF NOT EXISTS idx_analytics_weak_knowledge ON learning_analytics USING GIN (weak_knowledge_points);

-- ===============================================
-- 7. 創建/更新觸發器
-- ===============================================

-- 為新表添加 updated_at 觸發器
CREATE TRIGGER update_user_learning_profiles_updated_at 
    BEFORE UPDATE ON user_learning_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================
-- 8. 插入知識點主表測試數據
-- ===============================================

INSERT INTO knowledge_points_master (knowledge_point, subject, grade, chapter, difficulty_level, description) VALUES
-- 數學 8A 知識點
('一元一次方程式', '數學', '8A', '第1章 一元一次方程式', 'normal', '含有一個未知數的一次方程式'),
('移項運算', '數學', '8A', '第1章 一元一次方程式', 'easy', '方程式求解中的移項技巧'),
('分數方程式', '數學', '8A', '第1章 一元一次方程式', 'hard', '含有分數的一元一次方程式'),
('應用問題', '數學', '8A', '第1章 一元一次方程式', 'hard', '利用一元一次方程式解決實際問題'),
('代數運算', '數學', '8A', '第1章 一元一次方程式', 'normal', '基本的代數運算法則'),

-- 數學 7A 知識點
('正負數', '數學', '7A', '第1章 整數', 'easy', '正數、負數的概念和表示'),
('絕對值', '數學', '7A', '第1章 整數', 'normal', '數的絕對值概念和計算'),
('整數加減', '數學', '7A', '第1章 整數', 'normal', '正負整數的加法和減法運算'),

-- 英文知識點
('現在簡單式', '英文', '7A', '第1課 介紹自己', 'normal', '現在簡單式的用法和變化'),
('人稱代名詞', '英文', '7A', '第1課 介紹自己', 'easy', '主格人稱代名詞的使用'),
('be動詞', '英文', '7A', '第1課 介紹自己', 'easy', 'am, is, are 的正確使用'),

-- 國文知識點
('修辭技巧', '國文', '8A', '第1課 夏夜', 'normal', '各種修辭手法的認識和運用'),
('文意理解', '國文', '8A', '第1課 夏夜', 'normal', '文章內容的理解和分析'),
('字音字形', '國文', '8A', '第1課 夏夜', 'easy', '正確的字音和字形辨識')

ON CONFLICT (knowledge_point) DO NOTHING;

-- ===============================================
-- 9. 創建檢視表以便於查詢
-- ===============================================

-- 學習統計檢視
CREATE OR REPLACE VIEW learning_statistics_view AS
SELECT 
    ls.user_id,
    u.username,
    u.first_name,
    u.last_name,
    ls.subject,
    ls.grade,
    ls.publisher,
    COUNT(ls.id) as total_sessions,
    SUM(ls.question_count) as total_questions,
    SUM(ls.correct_count) as total_correct,
    ROUND(AVG(ls.accuracy_rate), 2) as avg_accuracy,
    SUM(ls.time_spent) as total_time_spent,
    MAX(ls.created_at) as last_practice_date
FROM learning_sessions ls
JOIN users u ON ls.user_id = u.id
WHERE ls.status = 'completed'
GROUP BY ls.user_id, u.username, u.first_name, u.last_name, ls.subject, ls.grade, ls.publisher;

-- 知識點掌握程度檢視
CREATE OR REPLACE VIEW knowledge_mastery_view AS
SELECT 
    er.user_id,
    er.subject,
    er.grade,
    UNNEST(er.knowledge_points) as knowledge_point,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END) as correct_attempts,
    ROUND(
        (SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
        2
    ) as mastery_rate
FROM exercise_records er
WHERE er.knowledge_points IS NOT NULL
GROUP BY er.user_id, er.subject, er.grade, UNNEST(er.knowledge_points)
HAVING COUNT(*) >= 3; -- 至少練習3次才統計

-- ===============================================
-- 10. 資料庫函數
-- ===============================================

-- 計算用戶在特定科目的掌握程度
CREATE OR REPLACE FUNCTION calculate_subject_mastery(
    p_user_id INTEGER,
    p_subject VARCHAR(50),
    p_grade VARCHAR(20)
) RETURNS TABLE (
    knowledge_point TEXT,
    mastery_rate DECIMAL(5,2),
    total_attempts INTEGER,
    last_practice_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        UNNEST(er.knowledge_points) as knowledge_point,
        ROUND(
            (SUM(CASE WHEN er.is_correct THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
            2
        ) as mastery_rate,
        COUNT(*)::INTEGER as total_attempts,
        MAX(er.created_at) as last_practice_date
    FROM exercise_records er
    WHERE er.user_id = p_user_id 
        AND er.subject = p_subject 
        AND er.grade = p_grade
        AND er.knowledge_points IS NOT NULL
    GROUP BY UNNEST(er.knowledge_points)
    HAVING COUNT(*) >= 2
    ORDER BY mastery_rate ASC;
END;
$$ LANGUAGE plpgsql;

-- 更新用戶學習檔案的函數
CREATE OR REPLACE FUNCTION update_user_learning_profile(
    p_user_id INTEGER
) RETURNS VOID AS $$
DECLARE
    session_count INTEGER;
    question_count INTEGER;
    correct_count INTEGER;
    total_time INTEGER;
    accuracy DECIMAL(5,2);
BEGIN
    -- 計算統計數據
    SELECT 
        COUNT(DISTINCT ls.id),
        COALESCE(SUM(ls.question_count), 0),
        COALESCE(SUM(ls.correct_count), 0),
        COALESCE(SUM(ls.time_spent), 0)
    INTO session_count, question_count, correct_count, total_time
    FROM learning_sessions ls
    WHERE ls.user_id = p_user_id AND ls.status = 'completed';
    
    -- 計算正確率
    IF question_count > 0 THEN
        accuracy := ROUND((correct_count::DECIMAL / question_count) * 100, 2);
    ELSE
        accuracy := 0;
    END IF;
    
    -- 插入或更新用戶學習檔案
    INSERT INTO user_learning_profiles (
        user_id, 
        total_sessions, 
        total_questions, 
        correct_questions, 
        overall_accuracy, 
        total_practice_time,
        last_practice_date,
        updated_at
    ) VALUES (
        p_user_id, 
        session_count, 
        question_count, 
        correct_count, 
        accuracy, 
        total_time,
        CURRENT_DATE,
        CURRENT_TIMESTAMP
    ) 
    ON CONFLICT (user_id) 
    DO UPDATE SET
        total_sessions = EXCLUDED.total_sessions,
        total_questions = EXCLUDED.total_questions,
        correct_questions = EXCLUDED.correct_questions,
        overall_accuracy = EXCLUDED.overall_accuracy,
        total_practice_time = EXCLUDED.total_practice_time,
        last_practice_date = EXCLUDED.last_practice_date,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- ===============================================
-- 11. 權限設置
-- ===============================================

-- 為應用用戶授權（如果存在的話）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aipe-tester') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "aipe-tester";
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "aipe-tester";
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO "aipe-tester";
    END IF;
END $$;

-- ===============================================
-- 升級完成提示
-- ===============================================

DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'InULearning 學習練習記錄系統資料庫升級完成！';
    RAISE NOTICE '版本: v1.0.0';
    RAISE NOTICE '新增功能:';
    RAISE NOTICE '✅ 完整的練習會話追蹤';
    RAISE NOTICE '✅ 詳細的練習記錄管理'; 
    RAISE NOTICE '✅ 知識點追蹤系統';
    RAISE NOTICE '✅ 用戶學習檔案管理';
    RAISE NOTICE '✅ 學習分析功能';
    RAISE NOTICE '✅ 高效能索引設計';
    RAISE NOTICE '✅ 檢視表和函數支援';
    RAISE NOTICE '==============================================';
END $$;