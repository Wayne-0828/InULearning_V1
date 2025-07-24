#!/usr/bin/env python3
"""
InULearning_V1 全面系統測試腳本
測試資料庫、後端服務和API端點的功能
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    """測試結果資料類別"""
    name: str
    success: bool
    message: str
    details: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None

class SystemTester:
    """系統測試器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: List[TestResult] = []
        self.services = {
            "auth-service": {"port": 8001, "health_url": "http://localhost:8001/health"},
            "learning-service": {"port": 8002, "health_url": "http://localhost:8002/health"},
            "question-bank-service": {"port": 8003, "health_url": "http://localhost:8003/health"},
            "ai-analysis-service": {"port": 8004, "health_url": "http://localhost:8004/health"}
        }
    
    def log_result(self, result: TestResult):
        """記錄測試結果"""
        self.results.append(result)
        status = "✅" if result.success else "❌"
        print(f"{status} {result.name}: {result.message}")
        if result.details:
            print(f"   詳情: {result.details}")
        if result.error:
            print(f"   錯誤: {result.error}")
        print()
    
    def test_environment(self) -> TestResult:
        """測試環境配置"""
        start_time = time.time()
        
        try:
            # 檢查 Python 版本
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                return TestResult(
                    name="環境檢查",
                    success=False,
                    message="Python 版本過低",
                    error=f"需要 Python 3.8+，當前版本: {python_version.major}.{python_version.minor}.{python_version.micro}"
                )
            
            # 檢查必要套件
            required_packages = ['requests', 'pytest', 'fastapi', 'sqlalchemy']
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                return TestResult(
                    name="環境檢查",
                    success=False,
                    message="缺少必要套件",
                    error=f"缺少套件: {', '.join(missing_packages)}"
                )
            
            duration = time.time() - start_time
            return TestResult(
                name="環境檢查",
                success=True,
                message="環境配置正確",
                details=f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="環境檢查",
                success=False,
                message="環境檢查失敗",
                error=str(e),
                duration=duration
            )
    
    def test_database_connections(self) -> TestResult:
        """測試資料庫連接"""
        start_time = time.time()
        
        try:
            # 測試 PostgreSQL
            import psycopg2
            postgres_ok = False
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="inulearning",
                    user="postgres",
                    password="password"
                )
                conn.close()
                postgres_ok = True
            except Exception as e:
                postgres_error = str(e)
            
            # 測試 MongoDB
            import pymongo
            mongo_ok = False
            try:
                client = pymongo.MongoClient("mongodb://localhost:27017/")
                client.admin.command('ping')
                client.close()
                mongo_ok = True
            except Exception as e:
                mongo_error = str(e)
            
            # 測試 Redis
            import redis
            redis_ok = False
            try:
                r = redis.Redis(host="localhost", port=6379, db=0)
                r.ping()
                r.close()
                redis_ok = True
            except Exception as e:
                redis_error = str(e)
            
            duration = time.time() - start_time
            
            if postgres_ok and mongo_ok and redis_ok:
                return TestResult(
                    name="資料庫連接",
                    success=True,
                    message="所有資料庫連接正常",
                    details="PostgreSQL, MongoDB, Redis 都連接成功",
                    duration=duration
                )
            else:
                errors = []
                if not postgres_ok:
                    errors.append(f"PostgreSQL: {postgres_error}")
                if not mongo_ok:
                    errors.append(f"MongoDB: {mongo_error}")
                if not redis_ok:
                    errors.append(f"Redis: {redis_error}")
                
                return TestResult(
                    name="資料庫連接",
                    success=False,
                    message="部分資料庫連接失敗",
                    error="; ".join(errors),
                    duration=duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="資料庫連接",
                success=False,
                message="資料庫連接測試失敗",
                error=str(e),
                duration=duration
            )
    
    def test_service_health(self) -> List[TestResult]:
        """測試服務健康狀態"""
        results = []
        
        for service_name, config in self.services.items():
            start_time = time.time()
            
            try:
                response = requests.get(config["health_url"], timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    results.append(TestResult(
                        name=f"{service_name} 健康檢查",
                        success=True,
                        message="服務正常運行",
                        details=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                else:
                    results.append(TestResult(
                        name=f"{service_name} 健康檢查",
                        success=False,
                        message="服務回應異常",
                        error=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                    
            except requests.exceptions.ConnectionError:
                duration = time.time() - start_time
                results.append(TestResult(
                    name=f"{service_name} 健康檢查",
                    success=False,
                    message="服務無法連接",
                    error="連接被拒絕，服務可能未啟動",
                    duration=duration
                ))
            except Exception as e:
                duration = time.time() - start_time
                results.append(TestResult(
                    name=f"{service_name} 健康檢查",
                    success=False,
                    message="健康檢查失敗",
                    error=str(e),
                    duration=duration
                ))
        
        return results
    
    def test_api_endpoints(self) -> List[TestResult]:
        """測試 API 端點"""
        results = []
        
        # 測試認證服務 API
        auth_endpoints = [
            ("POST", "/api/v1/auth/register", {"email": "test@example.com", "username": "testuser", "password": "testpass123", "role": "student"}),
            ("POST", "/api/v1/auth/login", {"email": "test@example.com", "password": "testpass123"}),
            ("GET", "/docs", None),
            ("GET", "/openapi.json", None)
        ]
        
        for method, endpoint, data in auth_endpoints:
            start_time = time.time()
            
            try:
                url = f"http://localhost:8001{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
                
                duration = time.time() - start_time
                
                # 對於某些端點，我們只檢查服務是否回應
                if response.status_code in [200, 201, 422, 401]:  # 422 是驗證錯誤，401 是認證錯誤
                    results.append(TestResult(
                        name=f"Auth API {method} {endpoint}",
                        success=True,
                        message="API 端點正常",
                        details=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                else:
                    results.append(TestResult(
                        name=f"Auth API {method} {endpoint}",
                        success=False,
                        message="API 端點異常",
                        error=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                    
            except Exception as e:
                duration = time.time() - start_time
                results.append(TestResult(
                    name=f"Auth API {method} {endpoint}",
                    success=False,
                    message="API 測試失敗",
                    error=str(e),
                    duration=duration
                ))
        
        # 測試其他服務的 API 文檔
        for service_name, config in self.services.items():
            if service_name == "auth-service":
                continue
                
            start_time = time.time()
            
            try:
                docs_url = f"http://localhost:{config['port']}/docs"
                response = requests.get(docs_url, timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    results.append(TestResult(
                        name=f"{service_name} API 文檔",
                        success=True,
                        message="API 文檔可存取",
                        details=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                else:
                    results.append(TestResult(
                        name=f"{service_name} API 文檔",
                        success=False,
                        message="API 文檔無法存取",
                        error=f"狀態碼: {response.status_code}",
                        duration=duration
                    ))
                    
            except Exception as e:
                duration = time.time() - start_time
                results.append(TestResult(
                    name=f"{service_name} API 文檔",
                    success=False,
                    message="API 文檔測試失敗",
                    error=str(e),
                    duration=duration
                ))
        
        return results
    
    def test_database_operations(self) -> TestResult:
        """測試資料庫基本操作"""
        start_time = time.time()
        
        try:
            # 測試 PostgreSQL 基本操作
            import psycopg2
            
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="inulearning",
                user="postgres",
                password="password"
            )
            
            cursor = conn.cursor()
            
            # 測試查詢
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result and result[0] == 1:
                duration = time.time() - start_time
                return TestResult(
                    name="資料庫操作",
                    success=True,
                    message="資料庫基本操作正常",
                    details="PostgreSQL 查詢測試通過",
                    duration=duration
                )
            else:
                duration = time.time() - start_time
                return TestResult(
                    name="資料庫操作",
                    success=False,
                    message="資料庫查詢異常",
                    error="查詢結果不符合預期",
                    duration=duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="資料庫操作",
                success=False,
                message="資料庫操作測試失敗",
                error=str(e),
                duration=duration
            )
    
    def run_unified_tests(self) -> TestResult:
        """執行統一測試套件"""
        start_time = time.time()
        
        try:
            # 切換到統一測試目錄
            test_dir = self.project_root / "unified_tests"
            
            # 執行測試
            result = subprocess.run(
                [sys.executable, "run_all_tests.py", "--test-types", "unit", "--skip-health-check"],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分鐘超時
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return TestResult(
                    name="統一測試套件",
                    success=True,
                    message="統一測試通過",
                    details=f"退出碼: {result.returncode}",
                    duration=duration
                )
            else:
                return TestResult(
                    name="統一測試套件",
                    success=False,
                    message="統一測試失敗",
                    error=f"退出碼: {result.returncode}\n{result.stderr}",
                    duration=duration
                )
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                name="統一測試套件",
                success=False,
                message="統一測試超時",
                error="測試執行超過 5 分鐘",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name="統一測試套件",
                success=False,
                message="統一測試執行失敗",
                error=str(e),
                duration=duration
            )
    
    def generate_report(self) -> str:
        """生成測試報告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.results)
        
        report = f"""
# InULearning_V1 系統測試報告

**測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**總測試數**: {total_tests}
**通過**: {passed_tests}
**失敗**: {failed_tests}
**成功率**: {(passed_tests/total_tests*100):.1f}%
**總執行時間**: {total_duration:.2f} 秒

## 測試結果詳情

"""
        
        for result in self.results:
            status = "✅ 通過" if result.success else "❌ 失敗"
            report += f"### {result.name}\n"
            report += f"- **狀態**: {status}\n"
            report += f"- **訊息**: {result.message}\n"
            if result.details:
                report += f"- **詳情**: {result.details}\n"
            if result.error:
                report += f"- **錯誤**: {result.error}\n"
            report += f"- **執行時間**: {result.duration:.3f} 秒\n\n"
        
        # 按服務分組統計
        service_stats = {}
        for result in self.results:
            if "service" in result.name.lower():
                service_name = result.name.split()[0]
                if service_name not in service_stats:
                    service_stats[service_name] = {"total": 0, "passed": 0}
                service_stats[service_name]["total"] += 1
                if result.success:
                    service_stats[service_name]["passed"] += 1
        
        if service_stats:
            report += "## 服務測試統計\n\n"
            for service, stats in service_stats.items():
                success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                report += f"- **{service}**: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        return report
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 InULearning_V1 全面系統測試")
        print("=" * 60)
        print()
        
        # 環境檢查
        result = self.test_environment()
        self.log_result(result)
        
        # 資料庫連接測試
        result = self.test_database_connections()
        self.log_result(result)
        
        # 服務健康檢查
        print("🏥 服務健康檢查...")
        health_results = self.test_service_health()
        for result in health_results:
            self.log_result(result)
        
        # API 端點測試
        print("🔗 API 端點測試...")
        api_results = self.test_api_endpoints()
        for result in api_results:
            self.log_result(result)
        
        # 資料庫操作測試
        result = self.test_database_operations()
        self.log_result(result)
        
        # 統一測試套件
        print("🧪 執行統一測試套件...")
        result = self.run_unified_tests()
        self.log_result(result)
        
        # 生成報告
        print("📊 生成測試報告...")
        report = self.generate_report()
        
        # 保存報告
        report_file = self.project_root / "test_report" / "system_test_report.md"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 輸出摘要
        print("\n" + "=" * 60)
        print("📊 測試摘要")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"總測試數: {total_tests}")
        print(f"通過: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失敗的測試:")
            for result in self.results:
                if not result.success:
                    print(f"  - {result.name}: {result.message}")
        
        print(f"\n📄 詳細報告已保存到: {report_file}")
        
        return passed_tests == total_tests

def main():
    """主函數"""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有測試通過！系統功能正常")
        sys.exit(0)
    else:
        print("\n⚠️  部分測試失敗，請檢查系統配置")
        sys.exit(1)

if __name__ == "__main__":
    main() 