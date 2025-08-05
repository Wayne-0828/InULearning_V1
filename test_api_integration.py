#!/usr/bin/env python3
"""
InU Learning 註冊功能 API 整合測試
測試實際的 API 端點功能（端口 8001）
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

class APIIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api/v1"  # 使用正確的端口
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, name: str, passed: bool, message: str, details: Dict = None):
        """記錄測試結果"""
        result = {
            "name": name,
            "passed": passed,
            "message": message,
            "details": details or {},
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")
        print(f"      {message}")
        if details:
            print(f"      詳情: {json.dumps(details, ensure_ascii=False, indent=6)}")
        print()

    def test_health_check(self) -> bool:
        """測試健康檢查端點"""
        print("🏥 測試健康檢查...")
        
        try:
            response = self.session.get("http://localhost:8001/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "健康檢查",
                    True,
                    "API 服務正常運行",
                    {"status_code": response.status_code, "response": data}
                )
                return True
            else:
                self.log_test(
                    "健康檢查",
                    False,
                    f"API 回應異常 (HTTP {response.status_code})",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "健康檢查",
                False,
                f"無法連接到 API 服務: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_valid_registrations(self):
        """測試有效角色註冊"""
        print("📝 測試有效角色註冊...")
        
        timestamp = int(time.time())
        
        test_users = [
            {
                "role": "student",
                "email": f"student_{timestamp}_1@test.com",
                "username": f"student_{timestamp}_1",
                "password": "TestPass123!",
                "first_name": "測試",
                "last_name": "學生"
            },
            {
                "role": "parent",
                "email": f"parent_{timestamp}_2@test.com",
                "username": f"parent_{timestamp}_2",
                "password": "TestPass123!",
                "first_name": "測試",
                "last_name": "家長"
            },
            {
                "role": "teacher",
                "email": f"teacher_{timestamp}_3@test.com",
                "username": f"teacher_{timestamp}_3",
                "password": "TestPass123!",
                "first_name": "測試",
                "last_name": "教師"
            }
        ]
        
        for user_data in test_users:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=user_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 201:
                    response_data = response.json()
                    self.log_test(
                        f"{user_data['role'].title()} 角色註冊",
                        True,
                        f"註冊成功: {response_data.get('message', 'OK')}",
                        {
                            "role": user_data['role'],
                            "email": user_data['email'],
                            "username": user_data['username']
                        }
                    )
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                    self.log_test(
                        f"{user_data['role'].title()} 角色註冊",
                        False,
                        f"註冊失敗 (HTTP {response.status_code}): {error_data.get('detail', 'Unknown error')}",
                        {
                            "status_code": response.status_code,
                            "role": user_data['role'],
                            "error": error_data
                        }
                    )
                    
            except Exception as e:
                self.log_test(
                    f"{user_data['role'].title()} 角色註冊",
                    False,
                    f"請求錯誤: {str(e)}",
                    {"error": str(e), "role": user_data['role']}
                )

    def test_admin_blocking(self):
        """測試管理員角色被阻擋"""
        print("🔒 測試管理員角色限制...")
        
        admin_data = {
            "role": "admin",
            "email": f"admin_{int(time.time())}@test.com",
            "username": f"admin_{int(time.time())}",
            "password": "TestPass123!",
            "first_name": "測試",
            "last_name": "管理員"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=admin_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [400, 422]:  # 422 是 Pydantic 驗證錯誤
                error_data = response.json()
                error_msg = str(error_data.get('detail', ''))
                
                if '管理員' in error_msg or 'admin' in error_msg.lower():
                    self.log_test(
                        "管理員角色限制",
                        True,
                        f"正確阻擋管理員註冊: {error_msg}",
                        {"status_code": response.status_code, "error_message": error_msg}
                    )
                else:
                    self.log_test(
                        "管理員角色限制",
                        False,
                        f"錯誤訊息不正確: {error_msg}",
                        {"status_code": response.status_code, "error_message": error_msg}
                    )
            else:
                self.log_test(
                    "管理員角色限制",
                    False,
                    f"未正確阻擋管理員註冊 (HTTP {response.status_code})",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test(
                "管理員角色限制",
                False,
                f"請求錯誤: {str(e)}",
                {"error": str(e)}
            )

    def test_validation_errors(self):
        """測試輸入驗證錯誤"""
        print("🎯 測試輸入驗證...")
        
        validation_tests = [
            {
                "name": "空白郵件",
                "data": {
                    "role": "student",
                    "email": "",
                    "username": f"test_{int(time.time())}",
                    "password": "TestPass123!",
                    "first_name": "測試",
                    "last_name": "用戶"
                }
            },
            {
                "name": "無效郵件格式",
                "data": {
                    "role": "student",
                    "email": "invalid-email-format",
                    "username": f"test_{int(time.time())}",
                    "password": "TestPass123!",
                    "first_name": "測試",
                    "last_name": "用戶"
                }
            },
            {
                "name": "短密碼",
                "data": {
                    "role": "student",
                    "email": f"test_{int(time.time())}@test.com",
                    "username": f"test_{int(time.time())}",
                    "password": "123",
                    "first_name": "測試",
                    "last_name": "用戶"
                }
            },
            {
                "name": "無效角色",
                "data": {
                    "role": "invalid_role",
                    "email": f"test_{int(time.time())}@test.com",
                    "username": f"test_{int(time.time())}",
                    "password": "TestPass123!",
                    "first_name": "測試",
                    "last_name": "用戶"
                }
            }
        ]
        
        for test_case in validation_tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code >= 400:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    self.log_test(
                        f"驗證測試: {test_case['name']}",
                        True,
                        f"正確拒絕無效資料: {error_data.get('detail', 'Validation error')}",
                        {"status_code": response.status_code}
                    )
                else:
                    self.log_test(
                        f"驗證測試: {test_case['name']}",
                        False,
                        f"未正確拒絕無效資料 (HTTP {response.status_code})",
                        {"status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_test(
                    f"驗證測試: {test_case['name']}",
                    False,
                    f"請求錯誤: {str(e)}",
                    {"error": str(e)}
                )

    def test_duplicate_prevention(self):
        """測試重複註冊防護"""
        print("🔄 測試重複註冊防護...")
        
        unique_id = int(time.time())
        duplicate_user = {
            "role": "student",
            "email": f"duplicate_{unique_id}@test.com",
            "username": f"duplicate_{unique_id}",
            "password": "TestPass123!",
            "first_name": "重複",
            "last_name": "測試"
        }
        
        try:
            # 第一次註冊
            response1 = self.session.post(
                f"{self.base_url}/auth/register",
                json=duplicate_user,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response1.status_code == 201:
                self.log_test(
                    "重複註冊 - 首次",
                    True,
                    "首次註冊成功",
                    {"status_code": response1.status_code}
                )
                
                # 第二次註冊（應該失敗）
                response2 = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=duplicate_user,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response2.status_code >= 400:
                    error_data = response2.json() if response2.headers.get('content-type', '').startswith('application/json') else {}
                    self.log_test(
                        "重複註冊 - 防護",
                        True,
                        f"正確阻擋重複註冊: {error_data.get('detail', 'Duplicate error')}",
                        {"status_code": response2.status_code}
                    )
                else:
                    self.log_test(
                        "重複註冊 - 防護",
                        False,
                        f"未阻擋重複註冊 (HTTP {response2.status_code})",
                        {"status_code": response2.status_code}
                    )
            else:
                self.log_test(
                    "重複註冊 - 首次",
                    False,
                    f"首次註冊失敗 (HTTP {response1.status_code})",
                    {"status_code": response1.status_code}
                )
                
        except Exception as e:
            self.log_test(
                "重複註冊測試",
                False,
                f"請求錯誤: {str(e)}",
                {"error": str(e)}
            )

    def generate_summary(self):
        """生成測試摘要"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        print("=" * 80)
        print("📊 API 整合測試摘要")
        print("=" * 80)
        print(f"測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"總測試數: {total}")
        print(f"通過: {passed} ✅")
        print(f"失敗: {failed} ❌")
        print(f"通過率: {(passed / total * 100):.1f}%" if total > 0 else "0%")
        
        if failed > 0:
            print("\n❌ 失敗的測試:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['name']}: {result['message']}")
        
        print("\n🎯 測試結論:")
        if failed == 0:
            print("  ✅ 所有 API 測試通過！註冊功能運作正常")
            print("  ✅ 前後端整合完成")
            print("  ✅ 安全機制有效運作")
        else:
            print(f"  ⚠️ 有 {failed} 個 API 測試失敗")
            print("  📋 建議檢查後端服務配置和資料庫連接")
        
        print("=" * 80)
        
        return failed == 0

def main():
    print("🚀 InU Learning 註冊功能 API 整合測試")
    print("=" * 80)
    
    tester = APIIntegrationTester()
    
    try:
        # 執行測試套件
        if not tester.test_health_check():
            print("❌ API 服務不可用，無法繼續測試")
            print("   請確認服務運行在 http://localhost:8001")
            return False
        
        tester.test_valid_registrations()
        tester.test_admin_blocking()
        tester.test_validation_errors()
        tester.test_duplicate_prevention()
        
        # 生成摘要
        success = tester.generate_summary()
        
        # 保存報告
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": tester.test_results,
            "summary": {
                "total": len(tester.test_results),
                "passed": sum(1 for r in tester.test_results if r["passed"]),
                "failed": sum(1 for r in tester.test_results if not r["passed"])
            }
        }
        
        with open('api_integration_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 API 測試報告已保存到: api_integration_report.json")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ 測試被用戶中斷")
        return False
    except Exception as e:
        print(f"💥 測試執行錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)