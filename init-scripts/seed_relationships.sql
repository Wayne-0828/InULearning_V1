BEGIN;

-- 1) 確保測試用使用者存在（密碼為 password123 的 bcrypt 範例）
INSERT INTO users (email, username, hashed_password, role, first_name, last_name, is_active, is_verified, created_at)
VALUES
 ('teacher01@test.com','teacher01','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','teacher','安','林',true,true,NOW()),
 ('teacher02@test.com','teacher02','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','teacher','明','陳',true,true,NOW()),
 ('student01@test.com','student01','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小明','王',true,true,NOW()),
 ('student02@test.com','student02','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小華','李',true,true,NOW()),
 ('student03@test.com','student03','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小美','張',true,true,NOW()),
 ('student04@test.com','student04','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小強','陳',true,true,NOW()),
 ('student05@test.com','student05','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小雅','林',true,true,NOW()),
 ('student06@test.com','student06','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','student','小安','周',true,true,NOW()),
 ('parent01@test.com','parent01','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','parent','大明','王',true,true,NOW()),
 ('parent02@test.com','parent02','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','parent','大華','李',true,true,NOW()),
 ('parent03@test.com','parent03','$2b$12$80NUNl/aAMIfCCfbqbRc7e0ADOB81Ibbv1LWHNe7FytsweVw5ySNm','parent','大美','張',true,true,NOW())
ON CONFLICT (email) DO NOTHING;

-- 2) 確保班級存在（避免重複，先刪關聯再重建班級）
-- 2.1 暫存目標班級
DROP TABLE IF EXISTS tmp_target_classes;
CREATE TEMP TABLE tmp_target_classes(class_name text);
INSERT INTO tmp_target_classes(class_name) VALUES ('七年三班'),('七年四班');

-- 2.2 找出既有要替換的班級 ID
DROP TABLE IF EXISTS tmp_old_classes;
CREATE TEMP TABLE tmp_old_classes AS
SELECT sc.id, sc.class_name FROM school_classes sc
JOIN tmp_target_classes t ON t.class_name = sc.class_name
WHERE sc.school_year='2024-2025';

-- 2.3 先刪除依賴關聯，避免外鍵衝突
DELETE FROM teacher_class_relations WHERE class_id IN (SELECT id FROM tmp_old_classes);
DELETE FROM student_class_relations WHERE class_id IN (SELECT id FROM tmp_old_classes);

-- 2.4 刪除舊班級
DELETE FROM school_classes WHERE id IN (SELECT id FROM tmp_old_classes);

-- 2.5 建立新班級
INSERT INTO school_classes (class_name, grade, school_year, is_active, created_at)
VALUES
 ('七年三班','7','2024-2025',true,NOW()),
 ('七年四班','7','2024-2025',true,NOW());

-- 3) 暫存我們關心的使用者與班級 ID
DROP TABLE IF EXISTS tmp_users;
CREATE TEMP TABLE tmp_users AS
SELECT email, id FROM users WHERE email IN (
 'teacher01@test.com','teacher02@test.com',
 'student01@test.com','student02@test.com','student03@test.com','student04@test.com','student05@test.com','student06@test.com',
 'parent01@test.com','parent02@test.com','parent03@test.com'
);

DROP TABLE IF EXISTS tmp_classes;
CREATE TEMP TABLE tmp_classes AS
SELECT class_name, id FROM school_classes WHERE class_name IN ('七年三班','七年四班') AND school_year='2024-2025';

-- 4) 教師-班級關係（清理重複後插入）
DELETE FROM teacher_class_relations tcr
USING tmp_users u, tmp_classes c
WHERE tcr.teacher_id = u.id AND tcr.class_id = c.id
  AND (
    (u.email='teacher01@test.com' AND c.class_name IN ('七年三班','七年四班'))
    OR (u.email='teacher02@test.com' AND c.class_name='七年三班')
  );

INSERT INTO teacher_class_relations (teacher_id, class_id, subject, is_active, created_at)
SELECT u.id, c.id, v.subj, true, NOW()
FROM (VALUES 
 ('teacher01@test.com','七年三班','數學'),
 ('teacher01@test.com','七年四班','數學'),
 ('teacher02@test.com','七年三班','自然')
) AS v(email, class_name, subj)
JOIN tmp_users u ON u.email = v.email
JOIN tmp_classes c ON c.class_name = v.class_name;

-- 5) 學生-班級關係（清理重複後插入）
DELETE FROM student_class_relations scr
USING tmp_users u, tmp_classes c
WHERE scr.student_id = u.id AND scr.class_id = c.id
  AND (
    (u.email IN ('student01@test.com','student02@test.com','student03@test.com') AND c.class_name='七年三班')
    OR (u.email IN ('student04@test.com','student05@test.com','student06@test.com') AND c.class_name='七年四班')
    OR (u.email='student01@test.com' AND c.class_name='七年四班')
  );

INSERT INTO student_class_relations (student_id, class_id, student_number, is_active, created_at)
SELECT u.id, c.id, v.stu_no, true, NOW()
FROM (VALUES 
 ('student01@test.com','七年三班','7A001'),
 ('student02@test.com','七年三班','7A002'),
 ('student03@test.com','七年三班','7A003'),
 ('student04@test.com','七年四班','7B001'),
 ('student05@test.com','七年四班','7B002'),
 ('student06@test.com','七年四班','7B003'),
 ('student01@test.com','七年四班','7B101')
) AS v(email, class_name, stu_no)
JOIN tmp_users u ON u.email = v.email
JOIN tmp_classes c ON c.class_name = v.class_name;

-- 6) 家長-學生關係（清理重複後插入）
DELETE FROM parent_child_relations pcr
USING tmp_users p, tmp_users s
WHERE pcr.parent_id = p.id AND pcr.child_id = s.id
  AND (
    (p.email='parent01@test.com' AND s.email IN ('student01@test.com','student04@test.com'))
    OR (p.email='parent02@test.com' AND s.email='student02@test.com')
    OR (p.email='parent03@test.com' AND s.email='student03@test.com')
  );

INSERT INTO parent_child_relations (parent_id, child_id, relationship_type, is_active, created_at)
SELECT p.id, s.id, v.rel, true, NOW()
FROM (VALUES
 ('parent01@test.com','student01@test.com','parent'),
 ('parent02@test.com','student02@test.com','parent'),
 ('parent03@test.com','student03@test.com','guardian'),
 ('parent01@test.com','student04@test.com','parent')
) AS v(p_email, s_email, rel)
JOIN tmp_users p ON p.email = v.p_email
JOIN tmp_users s ON s.email = v.s_email;

COMMIT;


