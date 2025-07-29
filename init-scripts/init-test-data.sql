-- InULearning 測試資料初始化腳本
-- 版本: v1.0.0
-- 作者: AIPE01_group2
-- 日期: 2024-12-19

-- 插入測試用戶（學生、家長、教師）
INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at) VALUES
-- 學生用戶
('11111111-1111-1111-1111-111111111111', 'student01', 'student01@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'student', true, NOW()),
('11111111-1111-1111-1111-111111111112', 'student02', 'student02@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'student', true, NOW()),
('11111111-1111-1111-1111-111111111113', 'student03', 'student03@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'student', true, NOW()),
('11111111-1111-1111-1111-111111111114', 'student04', 'student04@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'student', true, NOW()),
('11111111-1111-1111-1111-111111111115', 'student05', 'student05@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'student', true, NOW()),

-- 家長用戶
('22222222-2222-2222-2222-222222222221', 'parent01', 'parent01@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'parent', true, NOW()),
('22222222-2222-2222-2222-222222222222', 'parent02', 'parent02@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'parent', true, NOW()),
('22222222-2222-2222-2222-222222222223', 'parent03', 'parent03@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'parent', true, NOW()),

-- 教師用戶
('33333333-3333-3333-3333-333333333331', 'teacher01', 'teacher01@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'teacher', true, NOW()),
('33333333-3333-3333-3333-333333333332', 'teacher02', 'teacher02@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'teacher', true, NOW()),

-- 管理員用戶
('44444444-4444-4444-4444-444444444441', 'admin01', 'admin01@test.com', '$2b$12$LQv3c1yqBwkHrODDhf7OsudkjhKDaOGd1j3rQ1hCjKk4S.2uQ4z.2', 'admin', true, NOW());

-- 插入用戶檔案資料
INSERT INTO user_profiles (user_id, real_name, grade, school, phone, address, preferences, created_at) VALUES
-- 學生檔案
('11111111-1111-1111-1111-111111111111', '王小明', '8A', '台北市立中正國中', '0912345001', '台北市中正區', '{"preferred_difficulty": "normal", "study_reminders": true}', NOW()),
('11111111-1111-1111-1111-111111111112', '李小華', '8A', '台北市立中正國中', '0912345002', '台北市中正區', '{"preferred_difficulty": "normal", "study_reminders": true}', NOW()),
('11111111-1111-1111-1111-111111111113', '張小美', '8B', '台北市立中正國中', '0912345003', '台北市中正區', '{"preferred_difficulty": "easy", "study_reminders": true}', NOW()),
('11111111-1111-1111-1111-111111111114', '陳小強', '9A', '台北市立大安國中', '0912345004', '台北市大安區', '{"preferred_difficulty": "hard", "study_reminders": false}', NOW()),
('11111111-1111-1111-1111-111111111115', '林小雅', '9A', '台北市立大安國中', '0912345005', '台北市大安區', '{"preferred_difficulty": "normal", "study_reminders": true}', NOW()),

-- 家長檔案
('22222222-2222-2222-2222-222222222221', '王大明', NULL, NULL, '0912345101', '台北市中正區', '{"notification_preferences": "email", "dashboard_settings": "detailed"}', NOW()),
('22222222-2222-2222-2222-222222222222', '李大華', NULL, NULL, '0912345102', '台北市中正區', '{"notification_preferences": "sms", "dashboard_settings": "summary"}', NOW()),
('22222222-2222-2222-2222-222222222223', '張大美', NULL, NULL, '0912345103', '台北市大安區', '{"notification_preferences": "email", "dashboard_settings": "detailed"}', NOW()),

-- 教師檔案
('33333333-3333-3333-3333-333333333331', '林老師', NULL, '台北市立中正國中', '0912345201', '台北市中正區', '{"class_management_style": "interactive", "grading_preferences": "detailed"}', NOW()),
('33333333-3333-3333-3333-333333333332', '陳老師', NULL, '台北市立大安國中', '0912345202', '台北市大安區', '{"class_management_style": "traditional", "grading_preferences": "summary"}', NOW()),

-- 管理員檔案
('44444444-4444-4444-4444-444444444441', '系統管理員', NULL, NULL, '0912345301', '台北市信義區', '{"admin_level": "super", "dashboard_access": "full"}', NOW());

-- 創建班級資料表
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    school VARCHAR(200) NOT NULL,
    teacher_id UUID NOT NULL REFERENCES users(id),
    academic_year VARCHAR(20) NOT NULL DEFAULT '2024-2025',
    semester VARCHAR(10) NOT NULL DEFAULT '上學期',
    subject VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入班級資料
INSERT INTO classes (id, name, grade, school, teacher_id, subject) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '8A班數學', '8A', '台北市立中正國中', '33333333-3333-3333-3333-333333333331', '數學'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '8B班數學', '8B', '台北市立中正國中', '33333333-3333-3333-3333-333333333331', '數學'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', '9A班數學', '9A', '台北市立大安國中', '33333333-3333-3333-3333-333333333332', '數學');

-- 創建家長學生關聯表
CREATE TABLE IF NOT EXISTS parent_student_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES users(id),
    student_id UUID NOT NULL REFERENCES users(id),
    relationship VARCHAR(20) NOT NULL, -- '父親', '母親', '監護人'
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(parent_id, student_id)
);

-- 插入家長學生關聯
INSERT INTO parent_student_relationships (parent_id, student_id, relationship, verified) VALUES
-- 王大明是王小明和李小華的父親
('22222222-2222-2222-2222-222222222221', '11111111-1111-1111-1111-111111111111', '父親', true),
('22222222-2222-2222-2222-222222222221', '11111111-1111-1111-1111-111111111112', '父親', true),
-- 李大華是張小美的母親
('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111113', '母親', true),
-- 張大美是陳小強和林小雅的母親
('22222222-2222-2222-2222-222222222223', '11111111-1111-1111-1111-111111111114', '母親', true),
('22222222-2222-2222-2222-222222222223', '11111111-1111-1111-1111-111111111115', '母親', true);

-- 創建學生班級關聯表
CREATE TABLE IF NOT EXISTS student_class_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES users(id),
    class_id UUID NOT NULL REFERENCES classes(id),
    enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'transferred'
    UNIQUE(student_id, class_id)
);

-- 插入學生班級關聯
INSERT INTO student_class_enrollments (student_id, class_id) VALUES
-- 8A班學生
('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
('11111111-1111-1111-1111-111111111112', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
-- 8B班學生
('11111111-1111-1111-1111-111111111113', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
-- 9A班學生
('11111111-1111-1111-1111-111111111114', 'cccccccc-cccc-cccc-cccc-cccccccccccc'),
('11111111-1111-1111-1111-111111111115', 'cccccccc-cccc-cccc-cccc-cccccccccccc');

-- 插入範例學習會話資料
INSERT INTO learning_sessions (id, user_id, grade, subject, publisher, chapter, question_count, status, overall_score, start_time, end_time, created_at) VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', '8A', '數學', '南一', '1-1 一元一次方程式', 10, 'completed', 85.0, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '1 hour'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111112', '8A', '數學', '南一', '1-2 一元一次方程式的應用', 8, 'completed', 75.0, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1.5 hours', NOW() - INTERVAL '2 hours'),
('ffffffff-ffff-ffff-ffff-ffffffffffff', '11111111-1111-1111-1111-111111111113', '8B', '數學', '翰林', '1-1 一元一次方程式', 5, 'completed', 90.0, NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2.5 hours', NOW() - INTERVAL '3 hours');

-- 插入範例學習記錄
INSERT INTO learning_records (id, session_id, question_id, grade, subject, publisher, chapter, topic, knowledge_points, difficulty, user_answer, correct_answer, is_correct, score, time_spent, created_at) VALUES
-- 王小明的記錄
('rr111111-1111-1111-1111-111111111111', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'q_math_8a_001', '8A', '數學', '南一', '1-1 一元一次方程式', '一元一次方程式', ARRAY['方程式求解'], 'normal', 'A', 'A', true, 10.0, 120, NOW() - INTERVAL '1 hour'),
('rr111111-1111-1111-1111-111111111112', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'q_math_8a_002', '8A', '數學', '南一', '1-1 一元一次方程式', '一元一次方程式', ARRAY['移項運算'], 'normal', 'B', 'C', false, 0.0, 180, NOW() - INTERVAL '1 hour'),

-- 李小華的記錄
('rr222222-2222-2222-2222-222222222222', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'q_math_8a_003', '8A', '數學', '南一', '1-2 一元一次方程式的應用', '應用問題', ARRAY['文字題解法'], 'hard', 'A', 'A', true, 10.0, 240, NOW() - INTERVAL '2 hours'),
('rr222222-2222-2222-2222-222222222223', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'q_math_8a_004', '8A', '數學', '南一', '1-2 一元一次方程式的應用', '應用問題', ARRAY['速度時間問題'], 'hard', 'C', 'B', false, 0.0, 300, NOW() - INTERVAL '2 hours');

-- 插入用戶學習檔案
INSERT INTO user_learning_profiles (user_id, grade, subject, publisher, current_level, strength_areas, weakness_areas, total_practice_time, total_questions_answered, average_accuracy, last_practice_date, created_at) VALUES
('11111111-1111-1111-1111-111111111111', '8A', '數學', '南一', 6, ARRAY['基礎運算', '數字計算'], ARRAY['移項運算', '符號處理'], 120, 20, 75.5, NOW()::date - 1, NOW()),
('11111111-1111-1111-1111-111111111112', '8A', '數學', '南一', 7, ARRAY['邏輯推理', '文字理解'], ARRAY['速度計算', '複雜應用'], 80, 15, 82.3, NOW()::date - 1, NOW()),
('11111111-1111-1111-1111-111111111113', '8B', '數學', '翰林', 8, ARRAY['基礎運算', '圖形理解'], ARRAY['進階應用'], 45, 8, 90.0, NOW()::date - 1, NOW());

-- 顯示插入完成訊息
SELECT 'InULearning 測試資料初始化完成！' as message,
       COUNT(*) as total_users 
FROM users;

SELECT '測試帳號資訊:' as info;
SELECT 'student01@test.com / password123 (學生)' as login_info
UNION ALL
SELECT 'parent01@test.com / password123 (家長)'
UNION ALL  
SELECT 'teacher01@test.com / password123 (教師)'
UNION ALL
SELECT 'admin01@test.com / password123 (管理員)'; 