-- 測試資料庫初始化腳本
-- 創建測試資料庫
CREATE DATABASE IF NOT EXISTS inulearning_test;

-- 連接到測試資料庫
\c inulearning_test;

-- 創建測試用戶表 (如果不存在)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    grade VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入測試用戶
INSERT INTO users (username, email, password_hash, role, grade) VALUES
('test_student', 'student@test.com', 'hashed_password', 'student', '7A'),
('test_parent', 'parent@test.com', 'hashed_password', 'parent', NULL),
('test_teacher', 'teacher@test.com', 'hashed_password', 'teacher', NULL)
ON CONFLICT (username) DO NOTHING;

-- 創建學習會話表
CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL DEFAULT 'practice',
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(50),
    chapter VARCHAR(100),
    difficulty VARCHAR(20),
    question_count INTEGER NOT NULL,
    overall_score DECIMAL(5,2),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    time_spent INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建學習記錄表
CREATE TABLE IF NOT EXISTS learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id),
    question_id VARCHAR(100) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    publisher VARCHAR(50),
    chapter VARCHAR(100),
    topic VARCHAR(100),
    knowledge_points TEXT,
    difficulty VARCHAR(20),
    user_answer VARCHAR(10),
    correct_answer VARCHAR(10) NOT NULL,
    is_correct BOOLEAN,
    score DECIMAL(5,2),
    time_spent INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_status ON learning_sessions(status);
CREATE INDEX IF NOT EXISTS idx_learning_records_session_id ON learning_records(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_records_question_id ON learning_records(question_id);

echo "✅ 測試資料庫初始化腳本創建完成"

echo ""
echo "🎉 測試環境設置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 啟動 PostgreSQL 資料庫服務"
echo "2. 運行測試資料庫初始化: psql -U postgres -f test_environment/init_test_db.sql"
echo "3. 運行環境測試: python test_setup.py"
echo "4. 啟動服務: python run.py"
echo "5. 運行單元測試: pytest"
echo ""
echo "🔗 服務地址: http://localhost:8002"
echo "📚 API 文檔: http://localhost:8002/docs"
echo "📋 健康檢查: http://localhost:8002/health" 
