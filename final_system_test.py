#!/usr/bin/env python3   測試系統
"""
最終系統測試 - 階段D完整驗證
"""

import requests
import asyncio
import time
import json
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalSystemTest:
    """最終系統測試"""
    
    def __init__(self):
        self.services = {
            'nginx': 'http://localhost:80',
            'student_frontend': 'http://localhost:8080', 
            'auth_service': 'http://localhost:8001',
            'question_bank_service': 'http://localhost:8002',
            'learning_service': 'http://localhost:8003',
            'admin_frontend': 'http://localhost:8081',
            'parent_frontend': 'http://localhost:8082',
            'teacher_frontend': 'http://localhost:8083'
        }
    
    def test_all_services_health(self):
        """測試所有服務健康狀況"""
        logger.info("🏥 測試所有服務健康狀況...")
        
        results = {}
        
        for service, url in self.services.items():
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"  ✅ {service}: HTTP {response.status_code}")
                    
                    # 測試API服務的健康端點
                    if 'service' in service:
                        health_response = requests.get(f"{url}/health", timeout=5)
                        if health_response.status_code == 200:
                            health_data = health_response.json()
                            logger.info(f"    💚 健康檢查: {health_data.get('status', 'N/A')}")
                    
                    results[service] = True
                else:
                    logger.error(f"  ❌ {service}: HTTP {response.status_code}")
                    results[service] = False
                    
            except Exception as e:
                logger.error(f"  ❌ {service}: {e}")
                results[service] = False
        
        return results
    
    def test_question_bank_functionality(self):
        """測試題庫功能"""
        logger.info("\n📚 測試題庫功能...")
        
        base_url = self.services['question_bank_service']
        
        # 測試案例
        test_cases = [
            {
                'name': '檢查翰林英文題庫',
                'endpoint': '/api/v1/questions/check',
                'params': {'grade': '7A', 'edition': '翰林', 'subject': '英文'}
            },
            {
                'name': '獲取翰林英文題目',
                'endpoint': '/api/v1/questions/by-conditions',
                'params': {'grade': '7A', 'edition': '翰林', 'subject': '英文', 'questionCount': 5}
            },
            {
                'name': '檢查康軒國文題庫',
                'endpoint': '/api/v1/questions/check',
                'params': {'grade': '7A', 'edition': '康軒', 'subject': '國文'}
            }
        ]
        
        success_count = 0
        
        for test in test_cases:
            try:
                logger.info(f"  📝 {test['name']}...")
                response = requests.get(f"{base_url}{test['endpoint']}", params=test['params'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        if 'check' in test['endpoint']:
                            count = data['data']['count']
                            logger.info(f"    ✅ 找到 {count} 題")
                        else:
                            questions = data['data']
                            logger.info(f"    ✅ 獲取 {len(questions)} 題")
                            
                            # 檢查題目格式
                            if questions:
                                first_q = questions[0]
                                required_fields = ['id', 'question', 'options', 'answer']
                                missing = [f for f in required_fields if f not in first_q]
                                if not missing:
                                    logger.info(f"    ✅ 題目格式正確")
                                else:
                                    logger.warning(f"    ⚠️  缺少欄位: {missing}")
                        
                        success_count += 1
                    else:
                        logger.error(f"    ❌ API返回失敗: {data.get('error', 'Unknown')}")
                else:
                    logger.error(f"    ❌ HTTP錯誤: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"    ❌ 測試異常: {e}")
        
        return success_count == len(test_cases)
    
    def test_frontend_accessibility(self):
        """測試前端可訪問性"""
        logger.info("\n🌐 測試前端可訪問性...")
        
        frontend_urls = [
            ('學生前端主頁', f"{self.services['student_frontend']}/"),
            ('學生練習頁面', f"{self.services['student_frontend']}/pages/exercise.html"),
            ('學生考試頁面', f"{self.services['student_frontend']}/pages/exam.html"),
            ('管理員前端', f"{self.services['admin_frontend']}/"),
            ('家長前端', f"{self.services['parent_frontend']}/"),
            ('教師前端', f"{self.services['teacher_frontend']}/")
        ]
        
        success_count = 0
        
        for name, url in frontend_urls:
            try:
                logger.info(f"  📄 {name}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # 基本檢查：頁面包含HTML結構
                    content = response.text
                    if '<html' in content and '</html>' in content:
                        logger.info(f"    ✅ 頁面正常載入")
                        success_count += 1
                    else:
                        logger.warning(f"    ⚠️  頁面內容異常")
                else:
                    logger.error(f"    ❌ HTTP錯誤: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"    ❌ 測試異常: {e}")
        
        return success_count == len(frontend_urls)
    
    def test_end_to_end_workflow(self):
        """測試端到端工作流程"""
        logger.info("\n🔄 測試端到端工作流程...")
        
        try:
            base_url = self.services['question_bank_service']
            
            # 1. 檢查題庫
            logger.info("  1️⃣  檢查題庫可用性...")
            check_response = requests.get(
                f"{base_url}/api/v1/questions/check",
                params={'grade': '7A', 'edition': '翰林', 'subject': '英文'},
                timeout=10
            )
            
            if check_response.status_code != 200:
                logger.error("    ❌ 題庫檢查失敗")
                return False
            
            check_data = check_response.json()
            if not check_data.get('success') or check_data['data']['count'] == 0:
                logger.error("    ❌ 沒有可用題目")
                return False
            
            available_count = check_data['data']['count']
            logger.info(f"    ✅ 找到 {available_count} 題可用")
            
            # 2. 獲取題目
            logger.info("  2️⃣  獲取題目...")
            questions_response = requests.get(
                f"{base_url}/api/v1/questions/by-conditions",
                params={'grade': '7A', 'edition': '翰林', 'subject': '英文', 'questionCount': 3},
                timeout=10
            )
            
            if questions_response.status_code != 200:
                logger.error("    ❌ 題目獲取失敗")
                return False
            
            questions_data = questions_response.json()
            if not questions_data.get('success') or not questions_data['data']:
                logger.error("    ❌ 沒有獲取到題目")
                return False
            
            questions = questions_data['data']
            logger.info(f"    ✅ 成功獲取 {len(questions)} 題")
            
            # 3. 驗證題目內容
            logger.info("  3️⃣  驗證題目內容...")
            first_question = questions[0]
            
            # 檢查必要欄位
            required_fields = ['id', 'question', 'options', 'answer', 'subject', 'publisher', 'grade']
            missing_fields = [field for field in required_fields if field not in first_question]
            
            if missing_fields:
                logger.error(f"    ❌ 題目缺少欄位: {missing_fields}")
                return False
            
            logger.info(f"    ✅ 題目格式正確")
            logger.info(f"    📋 範例題目: {first_question['question'][:50]}...")
            logger.info(f"    📚 科目: {first_question['subject']}")
            logger.info(f"    🏢 出版社: {first_question['publisher']}")
            
            # 4. 測試前端頁面可訪問
            logger.info("  4️⃣  測試前端整合...")
            frontend_response = requests.get(
                f"{self.services['student_frontend']}/pages/exercise.html",
                timeout=10
            )
            
            if frontend_response.status_code != 200:
                logger.error("    ❌ 前端頁面不可訪問")
                return False
            
            logger.info(f"    ✅ 前端頁面可訪問")
            
            logger.info("  🎉 端到端工作流程測試通過！")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ 端到端測試異常: {e}")
            return False
    
    def run_final_test(self):
        """執行最終測試"""
        logger.info("🚀 開始最終系統測試...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 測試結果
        results = {}
        
        # 1. 服務健康檢查
        logger.info("\n📊 階段1/4: 服務健康檢查")
        service_health = self.test_all_services_health()
        healthy_services = sum(service_health.values())
        total_services = len(service_health)
        results['services'] = (healthy_services, total_services)
        
        # 2. 題庫功能測試
        logger.info("\n📊 階段2/4: 題庫功能測試")
        question_bank_ok = self.test_question_bank_functionality()
        results['question_bank'] = question_bank_ok
        
        # 3. 前端可訪問性測試
        logger.info("\n📊 階段3/4: 前端可訪問性測試")
        frontend_ok = self.test_frontend_accessibility()
        results['frontend'] = frontend_ok
        
        # 4. 端到端工作流程測試
        logger.info("\n📊 階段4/4: 端到端工作流程測試")
        e2e_ok = self.test_end_to_end_workflow()
        results['e2e_workflow'] = e2e_ok
        
        # 計算總耗時
        elapsed_time = time.time() - start_time
        
        # 生成最終報告
        self.generate_final_report(results, elapsed_time)
        
        # 判斷總體成功
        all_services_healthy = healthy_services == total_services
        all_functions_ok = all([question_bank_ok, frontend_ok, e2e_ok])
        
        return all_services_healthy and all_functions_ok
    
    def generate_final_report(self, results, elapsed_time):
        """生成最終報告"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 最終系統測試報告")
        logger.info("=" * 60)
        
        # 服務狀況
        healthy_services, total_services = results['services']
        logger.info(f"\n🏥 服務健康狀況: {healthy_services}/{total_services}")
        
        # 功能測試
        logger.info(f"\n🧪 功能測試結果:")
        function_tests = [
            ('題庫API', results['question_bank']),
            ('前端頁面', results['frontend']),
            ('端到端工作流程', results['e2e_workflow'])
        ]
        
        passed_functions = 0
        for name, result in function_tests:
            status = "✅" if result else "❌"
            logger.info(f"  {status} {name}")
            if result:
                passed_functions += 1
        
        # 統計
        logger.info(f"\n📈 測試統計:")
        logger.info(f"  服務健康率: {healthy_services/total_services*100:.1f}%")
        logger.info(f"  功能通過率: {passed_functions/len(function_tests)*100:.1f}%")
        logger.info(f"  總耗時: {elapsed_time:.2f} 秒")
        
        # 最終結果
        all_passed = (healthy_services == total_services and 
                     passed_functions == len(function_tests))
        
        if all_passed:
            logger.info(f"\n🎉 系統測試全部通過！")
            logger.info(f"✅ InULearning系統完全就緒，可以正常使用")
            logger.info(f"🚀 學生可以通過 http://localhost:8080 訪問練習系統")
        else:
            logger.info(f"\n⚠️  系統測試部分失敗")
            if healthy_services < total_services:
                logger.info(f"❌ 有 {total_services - healthy_services} 個服務不健康")
            if passed_functions < len(function_tests):
                logger.info(f"❌ 有 {len(function_tests) - passed_functions} 個功能測試失敗")
        
        return all_passed

def main():
    """主程式"""
    tester = FinalSystemTest()
    
    try:
        # 等待服務準備
        logger.info("⏳ 等待服務準備就緒...")
        time.sleep(3)
        
        # 執行最終測試
        success = tester.run_final_test()
        
        if success:
            logger.info(f"\n🎯 階段D測試完成：系統完全正常！")
            exit(0)
        else:
            logger.info(f"\n❌ 階段D測試完成：系統存在問題")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info(f"\n⏹️  測試被用戶中斷")
        exit(1)
    except Exception as e:
        logger.error(f"\n❌ 測試過程發生異常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()