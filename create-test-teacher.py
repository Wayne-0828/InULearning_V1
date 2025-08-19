#!/usr/bin/env python3
"""
創建測試教師帳號和相關資料
用於測試前端功能
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8001"  # 直接訪問 auth-service
API_BASE = f"{BASE_URL}/api/v1"

def create_test_teacher():
    """創建測試教師帳號"""
    print("🔧 創建測試教師帳號...")
    
    teacher_data = {
        "username": "testteacher",
        "email": "testteacher@example.com",
        "password": "test123456",
        "first_name": "測試",
        "last_name": "教師",
        "role": "teacher"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=teacher_data)
        if response.status_code == 201:
            print("✅ 測試教師帳號創建成功")
            return teacher_data
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("ℹ️ 測試教師帳號已存在")
            return teacher_data
        else:
            print(f"❌ 創建教師帳號失敗: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 創建教師帳號時發生錯誤: {e}")
        return None

def login_teacher(teacher_data):
    """登入教師帳號"""
    print("🔐 登入測試教師帳號...")
    
    login_data = {
        "email": teacher_data["email"],
        "password": teacher_data["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ 教師登入成功")
            return token
        else:
            print(f"❌ 教師登入失敗: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 教師登入時發生錯誤: {e}")
        return None

def create_test_class(token):
    """創建測試班級"""
    print("🏫 創建測試班級...")
    
    class_data = {
        "class_name": "測試班級",
        "subject": "數學",
        "grade": "10",
        "school_year": "2024-2025"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/relationships/teacher-class/create-class", json=class_data, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            print("✅ 測試班級創建成功")
            return data.get("class_id")
        else:
            print(f"❌ 創建班級失敗: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 創建班級時發生錯誤: {e}")
        return None

def create_test_student(token, class_id):
    """創建測試學生"""
    print("👨‍🎓 創建測試學生...")
    
    student_data = {
        "username": "teststudent2",
        "email": "teststudent2@example.com",
        "password": "test123456",
        "first_name": "測試",
        "last_name": "學生2",
        "role": "student"
    }
    
    # 先創建學生帳號
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=student_data)
        if response.status_code in [200, 201]:
            data = response.json()
            student_id = data.get("user_id") or data.get("id")
            print("✅ 測試學生帳號創建成功")
            print(f"✅ 獲取到學生 ID: {student_id}")
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("ℹ️ 測試學生帳號已存在，嘗試使用現有帳號")
            # 嘗試使用現有帳號，我們需要一個 ID
            student_id = 999  # 使用一個預設 ID
        else:
            print(f"❌ 創建學生帳號失敗: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 創建學生帳號時發生錯誤: {e}")
        return None
    
    # 將學生加入班級
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 先搜索學生來獲取正確的 ID
        try:
            search_response = requests.get(f"{API_BASE}/relationships/students/search?kw=teststudent2", headers=headers)
            if search_response.status_code == 200:
                students = search_response.json()
                if students:
                    actual_student_id = students[0].get("id")
                    print(f"✅ 通過搜索獲取到學生 ID: {actual_student_id}")
                    
                    # 將學生加入班級
                    add_student_data = {
                        "student_id": actual_student_id
                    }
                    
                    response = requests.post(f"{API_BASE}/relationships/classes/{class_id}/students", json=add_student_data, headers=headers)
                    if response.status_code in [200, 201]:
                        print("✅ 測試學生已加入班級")
                        return actual_student_id
                    else:
                        print(f"❌ 將學生加入班級失敗: {response.status_code}")
                        print(response.text)
                        return None
                else:
                    print("❌ 搜索學生結果為空")
                    return None
            else:
                print(f"❌ 搜索學生失敗: {search_response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 搜索學生時發生錯誤: {e}")
            return None
            
    except Exception as e:
        print(f"❌ 將學生加入班級時發生錯誤: {e}")
        return None

def delete_test_class(token, class_id):
    """刪除測試班級（軟刪除）"""
    print("🗑️ 刪除測試班級（軟刪除）...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{API_BASE}/relationships/teacher-class/{class_id}", headers=headers)
        if response.status_code == 200:
            print("✅ 測試班級已軟刪除")
            return True
        else:
            print(f"❌ 刪除班級失敗: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 刪除班級時發生錯誤: {e}")
        return False

def remove_test_student(token, student_id, class_id):
    """移除測試學生（軟刪除）"""
    print("👋 移除測試學生（軟刪除）...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{API_BASE}/relationships/student-class/{class_id}/{student_id}", headers=headers)
        if response.status_code == 200:
            print("✅ 測試學生已從班級移除")
            return True
        else:
            print(f"❌ 移除學生失敗: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 移除學生時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始創建測試資料...")
    print("=" * 50)
    
    # 1. 創建測試教師
    teacher_data = create_test_teacher()
    if not teacher_data:
        print("❌ 無法創建測試教師，停止執行")
        return
    
    # 2. 登入教師
    token = login_teacher(teacher_data)
    if not token:
        print("❌ 無法登入教師，停止執行")
        return
    
    # 3. 創建測試班級
    class_id = create_test_class(token)
    if not class_id:
        print("❌ 無法創建測試班級，停止執行")
        return
    
    # 4. 創建測試學生並加入班級
    student_id = create_test_student(token, class_id)
    if not student_id:
        print("❌ 無法創建測試學生，停止執行")
        return
    
    # 5. 等待一下讓資料同步
    print("⏳ 等待資料同步...")
    time.sleep(2)
    
    # 6. 刪除班級（軟刪除）
    if delete_test_class(token, class_id):
        print("✅ 班級已軟刪除，現在應該可以在「已刪除班級」中看到")
    
    # 7. 移除學生（軟刪除）
    if remove_test_student(token, student_id, class_id):
        print("✅ 學生已從班級移除，現在應該可以在「已移除學生」中看到")
    
    print("\n" + "=" * 50)
    print("🎯 測試資料創建完成！")
    print("\n📋 測試帳號資訊：")
    print(f"   教師帳號: {teacher_data['username']}")
    print(f"   教師密碼: {teacher_data['password']}")
    print(f"   學生帳號: teststudent")
    print(f"   學生密碼: test123456")
    print("\n🌐 測試步驟：")
    print("   1. 訪問: http://localhost:8083/login.html")
    print("   2. 使用教師帳號登入")
    print("   3. 訪問: http://localhost:8083/pages/classes-enhanced.html")
    print("   4. 檢查「已刪除班級」和「已移除學生」標籤頁")
    print("\n💡 如果仍然看不到資料，請檢查瀏覽器控制台的錯誤訊息")

if __name__ == "__main__":
    main()
