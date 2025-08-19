#!/usr/bin/env python3
"""
創建測試資料：已刪除的班級和已移除的學生
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 測試資料
TEST_CLASSES = [
    {
        "class_name": "測試班級-已刪除",
        "subject": "數學",
        "grade": "7",
        "school_year": "2024-2025"
    },
    {
        "class_name": "測試班級-活躍",
        "subject": "國文",
        "grade": "8",
        "school_year": "2024-2025"
    }
]

TEST_STUDENTS = [
    {
        "email": "test.student1@example.com",
        "first_name": "測試",
        "last_name": "學生1",
        "password": "test123",
        "role": "student"
    },
    {
        "email": "test.student2@example.com",
        "first_name": "測試",
        "last_name": "學生2",
        "password": "test123",
        "role": "student"
    }
]

def create_test_user(user_data):
    """創建測試用戶"""
    url = f"{API_BASE}/auth/register"
    
    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201:
            print(f"✅ 成功創建用戶: {user_data['email']}")
            return response.json()
        else:
            print(f"❌ 創建用戶失敗: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 創建用戶請求失敗: {e}")
        return None

def create_test_class(class_data):
    """創建測試班級"""
    url = f"{API_BASE}/relationships/teacher-class"
    
    try:
        response = requests.post(url, json=class_data)
        if response.status_code == 201:
            print(f"✅ 成功創建班級: {class_data['class_name']}")
            return response.json()
        else:
            print(f"❌ 創建班級失敗: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 創建班級請求失敗: {e}")
        return None

def add_student_to_class(class_id, student_id):
    """將學生加入班級"""
    url = f"{API_BASE}/relationships/student-class"
    
    try:
        data = {
            "class_id": class_id,
            "student_number": f"S{student_id:03d}"
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"✅ 成功將學生 {student_id} 加入班級 {class_id}")
            return response.json()
        else:
            print(f"❌ 加入學生失敗: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 加入學生請求失敗: {e}")
        return None

def delete_class(class_id):
    """刪除班級（軟刪除）"""
    url = f"{API_BASE}/relationships/teacher-class/{class_id}"
    
    try:
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"✅ 成功刪除班級: {class_id}")
            return True
        else:
            print(f"❌ 刪除班級失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 刪除班級請求失敗: {e}")
        return False

def remove_student_from_class(class_id, student_id):
    """從班級中移除學生（軟刪除）"""
    url = f"{API_BASE}/relationships/classes/{class_id}/students/{student_id}"
    
    try:
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"✅ 成功從班級 {class_id} 移除學生 {student_id}")
            return True
        else:
            print(f"❌ 移除學生失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 移除學生請求失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始創建測試資料")
    print("=" * 50)
    
    print("\n📋 注意事項:")
    print("1. 確保後端服務正在運行")
    print("2. 確保已經登入教師帳號")
    print("3. 這個腳本會創建測試資料，僅供開發測試使用")
    
    # 創建測試學生
    print("\n👥 創建測試學生...")
    student_ids = []
    for student_data in TEST_STUDENTS:
        result = create_test_user(student_data)
        if result and 'id' in result:
            student_ids.append(result['id'])
        time.sleep(1)  # 避免請求過快
    
    if not student_ids:
        print("❌ 無法創建測試學生，停止執行")
        return
    
    print(f"✅ 成功創建 {len(student_ids)} 個測試學生")
    
    # 創建測試班級
    print("\n🏫 創建測試班級...")
    class_ids = []
    for class_data in TEST_CLASSES:
        result = create_test_class(class_data)
        if result and 'id' in result:
            class_ids.append(result['id'])
        time.sleep(1)
    
    if not class_ids:
        print("❌ 無法創建測試班級，停止執行")
        return
    
    print(f"✅ 成功創建 {len(class_ids)} 個測試班級")
    
    # 將學生加入班級
    print("\n➕ 將學生加入班級...")
    for class_id in class_ids:
        for student_id in student_ids:
            add_student_to_class(class_id, student_id)
            time.sleep(1)
    
    # 刪除第一個班級（軟刪除）
    if len(class_ids) > 0:
        print(f"\n🗑️ 刪除班級 {class_ids[0]}（軟刪除）...")
        delete_class(class_ids[0])
    
    # 從第二個班級中移除第一個學生（軟刪除）
    if len(class_ids) > 1 and len(student_ids) > 0:
        print(f"\n👤 從班級 {class_ids[1]} 中移除學生 {student_ids[0]}（軟刪除）...")
        remove_student_from_class(class_ids[1], student_ids[0])
    
    print("\n" + "=" * 50)
    print("🎯 測試資料創建完成！")
    print(f"📊 創建的資料:")
    print(f"   - 學生: {len(student_ids)} 個")
    print(f"   - 班級: {len(class_ids)} 個")
    print(f"   - 已刪除班級: 1 個")
    print(f"   - 已移除學生: 1 個")
    print("\n現在可以測試前端頁面，應該能看到:")
    print("1. 在「已刪除班級」標籤頁中看到被刪除的班級")
    print("2. 在「已移除學生」標籤頁中看到被移除的學生")

if __name__ == "__main__":
    main()
