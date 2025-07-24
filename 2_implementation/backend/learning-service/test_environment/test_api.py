#!/usr/bin/env python3
"""
InULearning Learning Service API 測試腳本

用於測試 learning-service 的 API 端點
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx
from datetime import datetime

# 測試配置
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1"

# 測試用戶資訊
TEST_USER = {
    "username": "test_student",
    "email": "student@test.com",
    "role": "student",
    "grade": "7A"
}

# 模擬 JWT Token (實際使用時需要從 auth-service 獲取)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyLWlkIiwidXNlcm5hbWUiOiJ0ZXN0X3N0dWRlbnQiLCJyb2xlIjoic3R1ZGVudCIsImV4cCI6MTczNzE5MjAwMH0.test-signature"

class LearningServiceTester:
    """學習服務測試器"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            "Authorization": f"Bearer {TEST_TOKEN}",
            "Content-Type": "application/json"
        }
        self.test_results = []
    
    async def test_health_check(self) -> bool:
        """測試健康檢查端點"""
        print("🔍 測試健康檢查端點...")
        
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康檢查成功: {data}")
                self.test_results.append(("健康檢查", True, "成功"))
                return True
            else:
                print(f"❌ 健康檢查失敗: {response.status_code}")
                self.test_results.append(("健康檢查", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 健康檢查異常: {e}")
            self.test_results.append(("健康檢查", False, str(e)))
            return False
    
    async def test_create_exercise(self) -> bool:
        """測試創建練習會話"""
        print("🔍 測試創建練習會話...")
        
        exercise_data = {
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "chapter": "第一章",
            "difficulty": "normal",
            "question_count": 5,
            "knowledge_points": ["基礎運算", "代數概念"]
        }
        
        try:
            response = await self.client.post(
                f"{API_BASE}/exercises/create",
                json=exercise_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 創建練習成功: 會話ID = {data.get('session_id')}")
                self.test_results.append(("創建練習", True, f"會話ID: {data.get('session_id')}"))
                return data.get('session_id')
            elif response.status_code == 500:
                print("⚠️  創建練習失敗 (可能是外部服務不可用): 500")
                self.test_results.append(("創建練習", False, "外部服務不可用"))
                return None
            else:
                print(f"❌ 創建練習失敗: {response.status_code} - {response.text}")
                self.test_results.append(("創建練習", False, f"狀態碼: {response.status_code}"))
                return None
                
        except Exception as e:
            print(f"❌ 創建練習異常: {e}")
            self.test_results.append(("創建練習", False, str(e)))
            return None
    
    async def test_submit_answers(self, session_id: str) -> bool:
        """測試提交答案"""
        print("🔍 測試提交答案...")
        
        if not session_id:
            print("⚠️  跳過答案提交測試 (無會話ID)")
            self.test_results.append(("提交答案", False, "無會話ID"))
            return False
        
        answers_data = [
            {
                "question_id": "q1",
                "user_answer": "A",
                "time_spent": 120
            },
            {
                "question_id": "q2", 
                "user_answer": "B",
                "time_spent": 90
            },
            {
                "question_id": "q3",
                "user_answer": "C", 
                "time_spent": 150
            }
        ]
        
        try:
            response = await self.client.post(
                f"{API_BASE}/exercises/{session_id}/submit",
                json=answers_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 提交答案成功: 總分 = {data.get('overall_score')}")
                self.test_results.append(("提交答案", True, f"總分: {data.get('overall_score')}"))
                return True
            elif response.status_code == 500:
                print("⚠️  提交答案失敗 (可能是外部服務不可用): 500")
                self.test_results.append(("提交答案", False, "外部服務不可用"))
                return False
            else:
                print(f"❌ 提交答案失敗: {response.status_code} - {response.text}")
                self.test_results.append(("提交答案", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 提交答案異常: {e}")
            self.test_results.append(("提交答案", False, str(e)))
            return False
    
    async def test_get_sessions(self) -> bool:
        """測試獲取會話列表"""
        print("🔍 測試獲取會話列表...")
        
        try:
            response = await self.client.get(
                f"{API_BASE}/sessions/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 獲取會話列表成功: {len(data)} 個會話")
                self.test_results.append(("獲取會話列表", True, f"{len(data)} 個會話"))
                return True
            elif response.status_code == 401:
                print("⚠️  獲取會話列表失敗 (認證問題): 401")
                self.test_results.append(("獲取會話列表", False, "認證問題"))
                return False
            else:
                print(f"❌ 獲取會話列表失敗: {response.status_code}")
                self.test_results.append(("獲取會話列表", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 獲取會話列表異常: {e}")
            self.test_results.append(("獲取會話列表", False, str(e)))
            return False
    
    async def test_get_recommendations(self) -> bool:
        """測試獲取學習建議"""
        print("🔍 測試獲取學習建議...")
        
        try:
            response = await self.client.get(
                f"{API_BASE}/recommendations/learning",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 獲取學習建議成功: {len(data)} 個建議")
                self.test_results.append(("獲取學習建議", True, f"{len(data)} 個建議"))
                return True
            elif response.status_code == 401:
                print("⚠️  獲取學習建議失敗 (認證問題): 401")
                self.test_results.append(("獲取學習建議", False, "認證問題"))
                return False
            else:
                print(f"❌ 獲取學習建議失敗: {response.status_code}")
                self.test_results.append(("獲取學習建議", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 獲取學習建議異常: {e}")
            self.test_results.append(("獲取學習建議", False, str(e)))
            return False
    
    async def test_get_trends(self) -> bool:
        """測試獲取學習趨勢"""
        print("🔍 測試獲取學習趨勢...")
        
        try:
            response = await self.client.get(
                f"{API_BASE}/trends/learning",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 獲取學習趨勢成功: 趨勢 = {data.get('trend')}")
                self.test_results.append(("獲取學習趨勢", True, f"趨勢: {data.get('trend')}"))
                return True
            elif response.status_code == 401:
                print("⚠️  獲取學習趨勢失敗 (認證問題): 401")
                self.test_results.append(("獲取學習趨勢", False, "認證問題"))
                return False
            else:
                print(f"❌ 獲取學習趨勢失敗: {response.status_code}")
                self.test_results.append(("獲取學習趨勢", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 獲取學習趨勢異常: {e}")
            self.test_results.append(("獲取學習趨勢", False, str(e)))
            return False
    
    async def test_get_weekly_report(self) -> bool:
        """測試獲取週報告"""
        print("🔍 測試獲取週報告...")
        
        try:
            response = await self.client.get(
                f"{API_BASE}/trends/weekly-report",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 獲取週報告成功: 期間 = {data.get('period')}")
                self.test_results.append(("獲取週報告", True, f"期間: {data.get('period')}"))
                return True
            elif response.status_code == 401:
                print("⚠️  獲取週報告失敗 (認證問題): 401")
                self.test_results.append(("獲取週報告", False, "認證問題"))
                return False
            else:
                print(f"❌ 獲取週報告失敗: {response.status_code}")
                self.test_results.append(("獲取週報告", False, f"狀態碼: {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"❌ 獲取週報告異常: {e}")
            self.test_results.append(("獲取週報告", False, str(e)))
            return False
    
    def print_summary(self):
        """打印測試總結"""
        print("\n" + "=" * 60)
        print("📊 API 測試結果總結")
        print("=" * 60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✅ 通過" if success else "❌ 失敗"
            print(f"{test_name:<20} {status:<10} {message}")
            if success:
                passed += 1
        
        print("-" * 60)
        print(f"總計: {passed}/{total} 項測試通過")
        
        if passed == total:
            print("🎉 所有 API 測試通過！")
        elif passed >= total * 0.7:
            print("⚠️  大部分測試通過，部分功能可能受限於外部服務")
        else:
            print("❌ 多項測試失敗，請檢查服務狀態")
    
    async def close(self):
        """關閉客戶端"""
        await self.client.aclose()


async def main():
    """主函數"""
    print("🚀 InULearning Learning Service API 測試")
    print("=" * 60)
    print(f"📍 測試目標: {BASE_URL}")
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tester = LearningServiceTester()
    
    try:
        # 執行測試
        await tester.test_health_check()
        
        session_id = await tester.test_create_exercise()
        await tester.test_submit_answers(session_id)
        
        await tester.test_get_sessions()
        await tester.test_get_recommendations()
        await tester.test_get_trends()
        await tester.test_get_weekly_report()
        
    finally:
        await tester.close()
    
    # 打印總結
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main()) 