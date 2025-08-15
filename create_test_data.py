#!/usr/bin/env python3
"""
創建測試學習資料
"""

import json
import random
from datetime import datetime, timedelta

import requests

API_BASE = "http://localhost/api/v1"


def login_as_student(email="student01@test.com"):
    """登入學生帳號"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": "password123"},
            timeout=10,
        )

        if response.ok:
            return response.json().get("access_token")
        else:
            print(f"學生登入失敗: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"學生登入錯誤: {e}")
        return None


def create_learning_session(token, subject="數學", grade="7A"):
    """創建學習會話"""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        # 創建練習會話
        session_data = {
            "grade": grade,
            "edition": "翰林",
            "subject": subject,
            "chapter": "第一章",
            "questionCount": random.randint(5, 15),
        }

        response = requests.post(
            f"{API_BASE}/learning/exercises/create",
            json=session_data,
            headers=headers,
            timeout=10,
        )

        if response.ok:
            session_info = response.json()
            session_id = session_info.get("session_id")
            print(f"✅ 創建會話成功: {session_id}")
            return session_id
        else:
            print(f"❌ 創建會話失敗: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"❌ 創建會話錯誤: {e}")
        return None


def complete_session(token, session_id):
    """完成學習會話"""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        # 模擬答題結果
        score = random.randint(60, 100)
        correct_count = random.randint(3, 10)
        total_count = random.randint(5, 15)

        completion_data = {
            "session_id": session_id,
            "score": score,
            "correct_count": correct_count,
            "total_count": total_count,
            "time_spent": random.randint(300, 1800),  # 5-30 分鐘
            "completed_at": datetime.now().isoformat(),
        }

        response = requests.post(
            f"{API_BASE}/learning/exercises/complete",
            json=completion_data,
            headers=headers,
            timeout=10,
        )

        if response.ok:
            print(f"✅ 完成會話: {session_id} (分數: {score})")
            return True
        else:
            print(f"❌ 完成會話失敗: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ 完成會話錯誤: {e}")
        return False


def create_test_data():
    """創建測試資料"""
    print("🚀 開始創建測試學習資料")
    print("=" * 50)

    # 測試多個學生帳號
    students = ["student01@test.com", "student02@test.com", "student03@test.com"]

    subjects = ["數學", "國文", "英文", "自然"]
    grades = ["7A", "7B", "8A"]

    total_sessions = 0

    for student_email in students:
        print(f"\n👤 處理學生: {student_email}")

        # 登入學生
        token = login_as_student(student_email)
        if not token:
            print(f"   ⚠️ 跳過學生 {student_email}")
            continue

        # 為每個學生創建多個學習會話
        session_count = random.randint(3, 8)

        for i in range(session_count):
            subject = random.choice(subjects)
            grade = random.choice(grades)

            print(f"   📚 創建會話 {i+1}/{session_count}: {subject} ({grade})")

            # 創建會話
            session_id = create_learning_session(token, subject, grade)
            if session_id:
                # 完成會話
                if complete_session(token, session_id):
                    total_sessions += 1

    print("\n" + "=" * 50)
    print(f"📊 測試資料創建完成")
    print(f"✅ 總共創建了 {total_sessions} 個學習會話")
    print("\n🔍 現在可以測試學習記錄端點:")

    # 測試學習記錄端點
    teacher_token = login_teacher()
    if teacher_token:
        test_learning_records(teacher_token)


def login_teacher():
    """登入教師帳號"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "teacher01@test.com", "password": "password123"},
            timeout=10,
        )

        if response.ok:
            return response.json().get("access_token")
        else:
            return None

    except Exception as e:
        return None


def test_learning_records(token):
    """測試學習記錄"""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{API_BASE}/learning/records", headers=headers, timeout=10
        )

        if response.ok:
            data = response.json()
            print(f"📈 學習記錄查詢成功:")
            print(f"   - 總記錄數: {data.get('total', 0)}")
            print(f"   - 會話數: {len(data.get('sessions', []))}")

            if data.get("sessions"):
                print("   - 前 3 個會話:")
                for i, session in enumerate(data["sessions"][:3]):
                    print(
                        f"     {i+1}. 用戶: {session.get('user_name', 'N/A')}, "
                        f"科目: {session.get('subject', 'N/A')}, "
                        f"分數: {session.get('score', 'N/A')}"
                    )
        else:
            print(f"❌ 學習記錄查詢失敗: {response.status_code}")

    except Exception as e:
        print(f"❌ 學習記錄查詢錯誤: {e}")


if __name__ == "__main__":
    create_test_data()
