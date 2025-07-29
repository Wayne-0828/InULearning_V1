-- 關係管理測試數據初始化腳本

-- 創建班級數據
INSERT INTO school_classes (class_name, grade, school_year, is_active, created_at, updated_at) VALUES
('7A班', '7A', '2024-2025', true, NOW(), NOW()),
('7B班', '7B', '2024-2025', true, NOW(), NOW()),
('8A班', '8A', '2024-2025', true, NOW(), NOW()),
('8B班', '8B', '2024-2025', true, NOW(), NOW());

-- 創建家長-學生關係
-- 假設 parent01 是 student01 和 student02 的家長
INSERT INTO parent_child_relations (parent_id, child_id, relationship_type, is_active, created_at, updated_at) 
SELECT 
    p.id as parent_id,
    s.id as child_id,
    'parent' as relationship_type,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users p, users s 
WHERE p.username = 'parent01' AND p.role = 'parent'
  AND s.username IN ('student01', 'student02') AND s.role = 'student';

-- 創建教師-班級關係
-- teacher01 教授 7A班 的數學
INSERT INTO teacher_class_relations (teacher_id, class_id, subject, is_active, created_at, updated_at)
SELECT 
    t.id as teacher_id,
    c.id as class_id,
    '數學' as subject,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users t, school_classes c
WHERE t.username = 'teacher01' AND t.role = 'teacher'
  AND c.class_name = '7A班';

-- teacher01 也教授 7B班 的數學
INSERT INTO teacher_class_relations (teacher_id, class_id, subject, is_active, created_at, updated_at)
SELECT 
    t.id as teacher_id,
    c.id as class_id,
    '數學' as subject,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users t, school_classes c
WHERE t.username = 'teacher01' AND t.role = 'teacher'
  AND c.class_name = '7B班';

-- 創建學生-班級關係
-- student01 在 7A班
INSERT INTO student_class_relations (student_id, class_id, student_number, is_active, created_at, updated_at)
SELECT 
    s.id as student_id,
    c.id as class_id,
    '7A001' as student_number,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users s, school_classes c
WHERE s.username = 'student01' AND s.role = 'student'
  AND c.class_name = '7A班';

-- student02 在 7A班
INSERT INTO student_class_relations (student_id, class_id, student_number, is_active, created_at, updated_at)
SELECT 
    s.id as student_id,
    c.id as class_id,
    '7A002' as student_number,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users s, school_classes c
WHERE s.username = 'student02' AND s.role = 'student'
  AND c.class_name = '7A班';

-- student03 在 7B班
INSERT INTO student_class_relations (student_id, class_id, student_number, is_active, created_at, updated_at)
SELECT 
    s.id as student_id,
    c.id as class_id,
    '7B001' as student_number,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users s, school_classes c
WHERE s.username = 'student03' AND s.role = 'student'
  AND c.class_name = '7B班'; 