-- 教師端完整測試資料（可重複執行，具冪等性）
BEGIN;

-- 1) 確保教師存在（密碼 password123 的 bcrypt 範例）
INSERT INTO users (email, username, hashed_password, role, first_name, last_name, is_active, is_verified, created_at)
VALUES ('teacher01@test.com','teacher01','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','teacher','林','老師',true,true,NOW())
ON CONFLICT (email) DO NOTHING;

-- 2) 建立班級「七年一班」
INSERT INTO school_classes (class_name, grade, school_year, is_active, created_at)
VALUES ('七年一班','7','2024-2025', true, NOW())
ON CONFLICT DO NOTHING;

-- 3) 建立 10 位學生（密碼同上）
WITH hp AS (SELECT '$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm' AS h)
INSERT INTO users (email, username, hashed_password, role, is_active, first_name, last_name, created_at)
VALUES
('student01@test.com','student01',(SELECT h FROM hp),'student',true,'學生','01',NOW()),
('student02@test.com','student02',(SELECT h FROM hp),'student',true,'學生','02',NOW()),
('student03@test.com','student03',(SELECT h FROM hp),'student',true,'學生','03',NOW()),
('student04@test.com','student04',(SELECT h FROM hp),'student',true,'學生','04',NOW()),
('student05@test.com','student05',(SELECT h FROM hp),'student',true,'學生','05',NOW()),
('student06@test.com','student06',(SELECT h FROM hp),'student',true,'學生','06',NOW()),
('student07@test.com','student07',(SELECT h FROM hp),'student',true,'學生','07',NOW()),
('student08@test.com','student08',(SELECT h FROM hp),'student',true,'學生','08',NOW()),
('student09@test.com','student09',(SELECT h FROM hp),'student',true,'學生','09',NOW()),
('student10@test.com','student10',(SELECT h FROM hp),'student',true,'學生','10',NOW())
ON CONFLICT (email) DO NOTHING;

-- 4) 綁定 教師↔班級、學生↔班級
WITH t AS (
  SELECT id AS teacher_id FROM users WHERE email='teacher01@test.com'
), c AS (
  SELECT id AS class_id FROM school_classes WHERE class_name='七年一班' AND school_year='2024-2025'
)
INSERT INTO teacher_class_relations (teacher_id, class_id, subject, is_active, created_at)
SELECT t.teacher_id, c.class_id, '數學', true, NOW()
FROM t, c
WHERE NOT EXISTS (
  SELECT 1 FROM teacher_class_relations x WHERE x.teacher_id=t.teacher_id AND x.class_id=c.class_id AND x.is_active=true
);

WITH c AS (
  SELECT id AS class_id FROM school_classes WHERE class_name='七年一班' AND school_year='2024-2025'
), u AS (
  SELECT id, email FROM users WHERE email IN (
    'student01@test.com','student02@test.com','student03@test.com','student04@test.com','student05@test.com',
    'student06@test.com','student07@test.com','student08@test.com','student09@test.com','student10@test.com'
  )
)
INSERT INTO student_class_relations (student_id, class_id, student_number, is_active, created_at)
SELECT u.id, c.class_id, NULL, true, NOW()
FROM u, c
WHERE NOT EXISTS (
  SELECT 1 FROM student_class_relations s WHERE s.student_id=u.id AND s.class_id=c.class_id AND s.is_active=true
);

COMMIT;


