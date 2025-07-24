#!/usr/bin/env python3
"""
全端整合測試腳本
測試 Phase3 3.1 全端整合的所有新開發服務和功能
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# 測試配置
BASE_URL = "http://localhost:8000"
SERVICES = {
    "auth-service": "http://localhost:8001",
    "learning-service": "http://localhost:8002", 
    "question-bank-service": "http://localhost:8003",
    "ai-analysis-service": "http://localhost:8004",
    "parent-dashboard-service": "http://localhost:8005",
    "teacher-management-service": "http://localhost:8006",
    "notification-service": "http://localhost:8007"
}

class FullIntegrationTester:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.test_data = {}

    async def run_all_tests(self):
        """執行所有整合測試"""
        print("🚀 開始 Phase3 3.1 全端整合測試")
        print("=" * 60)
        
        # 1. 服務健康檢查
        await self.test_service_health()
        
        # 2. 認證服務測試
        await self.test_auth_service()
        
        # 3. 家長儀表板服務測試
        await self.test_parent_dashboard_service()
        
        # 4. 教師管理服務測試
        await self.test_teacher_management_service()
        
        # 5. 通知服務測試
        await self.test_notification_service()
        
        # 6. 跨服務整合測試
        await self.test_cross_service_integration()
        
        # 7. 前端整合測試
        await self.test_frontend_integration()
        
        # 輸出測試結果
        self.print_results()

    async def test_service_health(self):
        """測試所有服務的健康狀態"""
        print("\n📊 測試服務健康狀態...")
        
        for service_name, service_url in SERVICES.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{service_url}/health", timeout=10.0)
                    
                if response.status_code == 200:
                    self.log_success(f"✅ {service_name} 健康檢查通過")
                else:
                    self.log_error(f"❌ {service_name} 健康檢查失敗: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"❌ {service_name} 健康檢查錯誤: {str(e)}")

    async def test_auth_service(self):
        """測試認證服務"""
        print("\n🔐 測試認證服務...")
        
        # 測試用戶註冊
        try:
            async with httpx.AsyncClient() as client:
                # 註冊家長用戶
                parent_data = {
                    "username": "test_parent",
                    "email": "parent@test.com",
                    "password": "test123",
                    "role": "parent",
                    "name": "測試家長"
                }
                
                response = await client.post(
                    f"{SERVICES['auth-service']}/api/v1/auth/register",
                    json=parent_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    parent_user = response.json()
                    self.test_data["parent_user"] = parent_user
                    self.log_success("✅ 家長用戶註冊成功")
                else:
                    self.log_error(f"❌ 家長用戶註冊失敗: {response.status_code}")
                    return
                
                # 註冊教師用戶
                teacher_data = {
                    "username": "test_teacher",
                    "email": "teacher@test.com", 
                    "password": "test123",
                    "role": "teacher",
                    "name": "測試教師"
                }
                
                response = await client.post(
                    f"{SERVICES['auth-service']}/api/v1/auth/register",
                    json=teacher_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    teacher_user = response.json()
                    self.test_data["teacher_user"] = teacher_user
                    self.log_success("✅ 教師用戶註冊成功")
                else:
                    self.log_error(f"❌ 教師用戶註冊失敗: {response.status_code}")
                    return
                
                # 測試登入
                login_data = {
                    "username": "test_parent",
                    "password": "test123"
                }
                
                response = await client.post(
                    f"{SERVICES['auth-service']}/api/v1/auth/login",
                    json=login_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    login_result = response.json()
                    self.test_data["parent_token"] = login_result["access_token"]
                    self.log_success("✅ 家長用戶登入成功")
                else:
                    self.log_error(f"❌ 家長用戶登入失敗: {response.status_code}")
                    
        except Exception as e:
            self.log_error(f"❌ 認證服務測試錯誤: {str(e)}")

    async def test_parent_dashboard_service(self):
        """測試家長儀表板服務"""
        print("\n👨‍👩‍👧‍👦 測試家長儀表板服務...")
        
        if not self.test_data.get("parent_token"):
            self.log_error("❌ 缺少家長認證令牌，跳過家長儀表板測試")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['parent_token']}"}
            
            async with httpx.AsyncClient() as client:
                # 測試獲取子女列表
                response = await client.get(
                    f"{SERVICES['parent-dashboard-service']}/api/v1/parent/children",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    children = response.json()
                    self.log_success(f"✅ 獲取子女列表成功，共 {len(children)} 個子女")
                else:
                    self.log_error(f"❌ 獲取子女列表失敗: {response.status_code}")
                
                # 測試獲取家長儀表板
                response = await client.get(
                    f"{SERVICES['parent-dashboard-service']}/api/v1/parent/dashboard",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    dashboard = response.json()
                    self.log_success("✅ 獲取家長儀表板成功")
                else:
                    self.log_error(f"❌ 獲取家長儀表板失敗: {response.status_code}")
                    
        except Exception as e:
            self.log_error(f"❌ 家長儀表板服務測試錯誤: {str(e)}")

    async def test_teacher_management_service(self):
        """測試教師管理服務"""
        print("\n👨‍🏫 測試教師管理服務...")
        
        # 先獲取教師令牌
        try:
            async with httpx.AsyncClient() as client:
                login_data = {
                    "username": "test_teacher",
                    "password": "test123"
                }
                
                response = await client.post(
                    f"{SERVICES['auth-service']}/api/v1/auth/login",
                    json=login_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    login_result = response.json()
                    teacher_token = login_result["access_token"]
                    self.log_success("✅ 教師用戶登入成功")
                else:
                    self.log_error(f"❌ 教師用戶登入失敗: {response.status_code}")
                    return
                
                headers = {"Authorization": f"Bearer {teacher_token}"}
                
                # 測試獲取班級列表
                response = await client.get(
                    f"{SERVICES['teacher-management-service']}/api/v1/teacher/classes",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    classes = response.json()
                    self.log_success(f"✅ 獲取班級列表成功，共 {len(classes)} 個班級")
                else:
                    self.log_error(f"❌ 獲取班級列表失敗: {response.status_code}")
                
                # 測試獲取教師儀表板
                response = await client.get(
                    f"{SERVICES['teacher-management-service']}/api/v1/teacher/dashboard",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    dashboard = response.json()
                    self.log_success("✅ 獲取教師儀表板成功")
                else:
                    self.log_error(f"❌ 獲取教師儀表板失敗: {response.status_code}")
                    
        except Exception as e:
            self.log_error(f"❌ 教師管理服務測試錯誤: {str(e)}")

    async def test_notification_service(self):
        """測試通知服務"""
        print("\n📢 測試通知服務...")
        
        if not self.test_data.get("parent_token"):
            self.log_error("❌ 缺少認證令牌，跳過通知服務測試")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['parent_token']}"}
            
            async with httpx.AsyncClient() as client:
                # 測試獲取通知模板
                response = await client.get(
                    f"{SERVICES['notification-service']}/api/v1/notifications/templates",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    templates = response.json()
                    self.log_success(f"✅ 獲取通知模板成功，共 {len(templates)} 個模板")
                else:
                    self.log_error(f"❌ 獲取通知模板失敗: {response.status_code}")
                
                # 測試創建通知
                notification_data = {
                    "user_id": 1,
                    "notification_type": "learning_reminder",
                    "title": "學習提醒",
                    "message": "今天是學習的好日子！",
                    "priority": "normal"
                }
                
                response = await client.post(
                    f"{SERVICES['notification-service']}/api/v1/notifications",
                    json=notification_data,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    notification = response.json()
                    self.log_success("✅ 創建通知成功")
                else:
                    self.log_error(f"❌ 創建通知失敗: {response.status_code}")
                    
        except Exception as e:
            self.log_error(f"❌ 通知服務測試錯誤: {str(e)}")

    async def test_cross_service_integration(self):
        """測試跨服務整合"""
        print("\n🔗 測試跨服務整合...")
        
        try:
            # 測試家長儀表板與學習服務的整合
            if self.test_data.get("parent_token"):
                headers = {"Authorization": f"Bearer {self.test_data['parent_token']}"}
                
                async with httpx.AsyncClient() as client:
                    # 測試獲取子女學習進度
                    response = await client.get(
                        f"{SERVICES['parent-dashboard-service']}/api/v1/parent/children/1/progress",
                        headers=headers,
                        timeout=15.0
                    )
                    
                    if response.status_code == 200:
                        progress = response.json()
                        self.log_success("✅ 跨服務整合測試成功 - 家長儀表板與學習服務")
                    else:
                        self.log_error(f"❌ 跨服務整合測試失敗: {response.status_code}")
                        
        except Exception as e:
            self.log_error(f"❌ 跨服務整合測試錯誤: {str(e)}")

    async def test_frontend_integration(self):
        """測試前端整合"""
        print("\n🌐 測試前端整合...")
        
        frontend_apps = [
            ("學生應用", "http://localhost:3000"),
            ("家長應用", "http://localhost:3001"),
            ("教師應用", "http://localhost:3002"),
            ("管理員應用", "http://localhost:3003")
        ]
        
        for app_name, app_url in frontend_apps:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(app_url, timeout=10.0)
                    
                if response.status_code == 200:
                    self.log_success(f"✅ {app_name} 前端可訪問")
                else:
                    self.log_error(f"❌ {app_name} 前端訪問失敗: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"❌ {app_name} 前端測試錯誤: {str(e)}")

    def log_success(self, message: str):
        """記錄成功訊息"""
        print(f"  {message}")
        self.results["passed"] += 1
        self.results["total_tests"] += 1

    def log_error(self, message: str):
        """記錄錯誤訊息"""
        print(f"  {message}")
        self.results["failed"] += 1
        self.results["total_tests"] += 1
        self.results["errors"].append(message)

    def print_results(self):
        """輸出測試結果"""
        print("\n" + "=" * 60)
        print("📋 Phase3 3.1 全端整合測試結果")
        print("=" * 60)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"總測試數: {total}")
        print(f"通過: {passed} ✅")
        print(f"失敗: {failed} ❌")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ 失敗的測試:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("🎉 所有測試通過！Phase3 3.1 全端整合完成！")
        else:
            print("⚠️  部分測試失敗，請檢查相關服務和配置")

async def main():
    """主函數"""
    tester = FullIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 