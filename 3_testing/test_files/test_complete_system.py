#!/usr/bin/env python3
"""
完整系統測試 - 階段D
測試整個InULearning系統的完整功能
"""

import requests
import asyncio
import time
import json
from pathlib import Path
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemTester:
    """系統測試器"""
    
    def __init__(self):
        self.base_urls = {
            'nginx': 'http://localhost:80',
            'student_frontend': 'http://localhost:8080',
            'auth_service': 'http://localhost:8001',
            'question_bank_service': 'http://localhost:8002',
            'learning_service': 'http://localhost:8003',
            'admin_frontend': 'http://localhost:8081',
            'parent_frontend': 'http://localhost:8082',
            'teacher_frontend': 'http://localhost:8083'
        }
        
        self.test_results = {}
        
    def test_service_health(self, service_name, url):
        """測試服務健康狀況"""
        logger.info(f"🔍 測試 {service_name} 健康狀況...")
        
        try:
            # 測試基本連接
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ {service_name} 連接正常 (狀態碼: {response.status_code})")
                
                # 如果是API服務，測試健康檢查端點
                if 'service' in service_name:
                    health_url = f"{url}/health"
                    try:
                        health_response = requests.get(health_url, timeout=5)
                        if health_response.status_code == 200:
                            health_data = health_response.json()
                            logger.info(f"✅ {service_name} 健康檢查通過: {health_data.get('status', 'N/A')}")
                            return True
                        else:
                            logger.warning(f"⚠️  {service_name} 健康檢查失敗: {health_response.status_code}")
                            return False
                    except Exception as e:
                        logger.warning(f"⚠️  {service_name} 健康檢查異常: {e}")
                        return False
                else:
                    return True
            else:
                logger.error(f"❌ {service_name} 連接失敗 (狀態碼: {response.status_code})")
                return False
                
        except Exception as e:
            logger.error(f"❌ {service_name} 連接異常: {e}")
            return False
    
    def test_question_bank_api(self):
        """測試題庫API功能"""
        logger.info(f"\n🔍 測試題庫API功能...")
        
        base_url = self.base_urls['question_bank_service']
        
        # 測試案例
        test_cases = [
            {
                'name': '翰林英文題庫檢查',
                'url': f"{base_url}/api/v1/questions/check",
                'params': {'grade': '7A', 'edition': '翰林', 'subject': '英文'}
            },
            {
                'name': '康軒國文題庫檢查', 
                'url': f"{base_url}/api/v1/questions/check",
                'params': {'grade': '7A', 'edition': '康軒', 'subject': '國文'}
            },
            {
                'name': '獲取翰林英文題目',
                'url': f"{base_url}/api/v1/questions/by-conditions",
                'params': {'grade': '7A', 'edition': '翰林', 'subject': '英文', 'questionCount': 3}
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                logger.info(f"  📝 {test_case['name']}...")
                response = requests.get(test_case['url'], params=test_case['params'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        if 'check' in test_case['url']:
                            count = data['data']['count']
                            logger.info(f"    ✅ 成功，找到 {count} 題")
                        else:
                            questions = data['data']
                            logger.info(f"    ✅ 成功，獲取 {len(questions)} 題")
                            
                            # 檢查第一題的內容
                            if questions:
                                first_q = questions[0]
                                logger.info(f"    📋 第一題: {first_q.get('question', 'N/A')[:50]}...")
                                logger.info(f"    📸 圖片檔名: {first_q.get('image_filename', 'N/A')}")
                        
                        results.append(True)
                    else:
                        logger.error(f"    ❌ API返回失敗: {data.get('error', 'Unknown error')}")
                        results.append(False)
                else:
                    logger.error(f"    ❌ HTTP錯誤: {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                logger.error(f"    ❌ 測試異常: {e}")
                results.append(False)
        
        return all(results)
    
    def test_image_api(self):
        """測試圖片API功能"""
        logger.info(f"\n🔍 測試圖片API功能...")
        
        base_url = self.base_urls['question_bank_service']
        
        try:
            # 先獲取一個有圖片的題目
            response = requests.get(
                f"{base_url}/api/v1/questions/by-conditions",
                params={'grade': '7A', 'edition': '翰林', 'subject': '英文', 'questionCount': 10},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data['data']:
                    # 找一個有圖片的題目
                    questions_with_image = [q for q in data['data'] if q.get('image_filename')]
                    
                    if questions_with_image:
                        test_question = questions_with_image[0]
                        image_filename = test_question['image_filename']
                        
                        logger.info(f"  📸 測試圖片: {image_filename}")
                        
                        # 測試圖片檢查API
                        check_url = f"{base_url}/api/v1/images/check/{image_filename}"
                        check_response = requests.get(check_url, timeout=5)
                        
                        if check_response.status_code == 200:
                            logger.info(f"    ✅ 圖片檢查API正常")
                            
                            # 測試圖片獲取API
                            get_url = f"{base_url}/api/v1/images/{image_filename}"
                            get_response = requests.get(get_url, timeout=10)
                            
                            if get_response.status_code == 200:
                                image_size = len(get_response.content)
                                content_type = get_response.headers.get('Content-Type', 'N/A')
                                logger.info(f"    ✅ 圖片獲取API正常 (大小: {image_size} bytes, 類型: {content_type})")
                                return True
                            else:
                                logger.error(f"    ❌ 圖片獲取API失敗: {get_response.status_code}")
                                return False
                        else:
                            logger.error(f"    ❌ 圖片檢查API失敗: {check_response.status_code}")
                            return False
                    else:
                        logger.warning(f"    ⚠️  沒有找到有圖片的題目")
                        return True  # 不算失敗，可能是正常情況
                else:
                    logger.error(f"    ❌ 無法獲取題目來測試圖片")
                    return False
            else:
                logger.error(f"    ❌ 無法獲取題目: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"    ❌ 圖片API測試異常: {e}")
            return False
    
    def test_frontend_pages(self):
        """測試前端頁面"""
        logger.info(f"\n🔍 測試前端頁面...")
        
        frontend_tests = [
            {
                'name': '學生前端主頁',
                'url': f"{self.base_urls['student_frontend']}/",
                'expected_content': ['InU Learning', '練習']
            },
            {
                'name': '學生練習頁面',
                'url': f"{self.base_urls['student_frontend']}/pages/exercise.html",
                'expected_content': ['練習測驗', '年級', '版本']
            },
            {
                'name': '學生考試頁面',
                'url': f"{self.base_urls['student_frontend']}/pages/exam.html", 
                'expected_content': ['練習作答', '題目']
            }
        ]
        
        results = []
        
        for test in frontend_tests:
            try:
                logger.info(f"  📄 {test['name']}...")
                response = requests.get(test['url'], timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # 檢查預期內容
                    content_found = all(expected in content for expected in test['expected_content'])
                    
                    if content_found:
                        logger.info(f"    ✅ 頁面正常，包含預期內容")
                        results.append(True)
                    else:
                        logger.warning(f"    ⚠️  頁面載入但缺少預期內容")
                        results.append(False)
                else:
                    logger.error(f"    ❌ 頁面載入失敗: {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                logger.error(f"    ❌ 頁面測試異常: {e}")
                results.append(False)
        
        return all(results)
    
    def test_end_to_end_workflow(self):
        """測試端到端工作流程"""
        logger.info(f"\n🔍 測試端到端工作流程...")
        
        try:
            # 1. 檢查題庫
            logger.info(f"  1️⃣  檢查題庫...")
            check_response = requests.get(
                f"{self.base_urls['question_bank_service']}/api/v1/questions/check",
                params={'grade': '7A', 'edition': '翰林', 'subject': '英文'},
                timeout=10
            )
            
            if check_response.status_code != 200:
                logger.error(f"    ❌ 題庫檢查失敗")
                return False
            
            check_data = check_response.json()
            if not check_data.get('success') or check_data['data']['count'] == 0:
                logger.error(f"    ❌ 沒有可用題目")
                return False
            
            available_count = check_data['data']['count']
            logger.info(f"    ✅ 找到 {available_count} 題可用")
            
            # 2. 獲取題目
            logger.info(f"  2️⃣  獲取題目...")
            questions_response = requests.get(
                f"{self.base_urls['question_bank_service']}/api/v1/questions/by-conditions",
                params={'grade': '7A', 'edition': '翰林', 'subject': '英文', 'questionCount': 5},
                timeout=10
            )
            
            if questions_response.status_code != 200:
                logger.error(f"    ❌ 題目獲取失敗")
                return False
            
            questions_data = questions_response.json()
            if not questions_data.get('success') or not questions_data['data']:
                logger.error(f"    ❌ 沒有獲取到題目")
                return False
            
            questions = questions_data['data']
            logger.info(f"    ✅ 成功獲取 {len(questions)} 題")
            
            # 3. 驗證題目格式
            logger.info(f"  3️⃣  驗證題目格式...")
            required_fields = ['id', 'question', 'options', 'answer', 'subject', 'publisher', 'grade']
            
            for i, question in enumerate(questions):
                missing_fields = [field for field in required_fields if field not in question]
                if missing_fields:
                    logger.error(f"    ❌ 題目 {i+1} 缺少欄位: {missing_fields}")
                    return False
            
            logger.info(f"    ✅ 所有題目格式正確")
            
            # 4. 測試圖片（如果有的話）
            logger.info(f"  4️⃣  測試圖片...")
            questions_with_image = [q for q in questions if q.get('image_filename')]
            
            if questions_with_image:
                test_image = questions_with_image[0]['image_filename']
                image_response = requests.get(
                    f"{self.base_urls['question_bank_service']}/api/v1/images/{test_image}",
                    timeout=10
                )
                
                if image_response.status_code == 200:
                    logger.info(f"    ✅ 圖片載入正常 ({len(image_response.content)} bytes)")
                else:
                    logger.warning(f"    ⚠️  圖片載入失敗: {image_response.status_code}")
            else:
                logger.info(f"    ℹ️  此批題目沒有圖片")
            
            # 5. 測試前端整合
            logger.info(f"  5️⃣  測試前端整合...")
            frontend_response = requests.get(
                f"{self.base_urls['student_frontend']}/pages/exercise.html",
                timeout=10
            )
            
            if frontend_response.status_code == 200:
                logger.info(f"    ✅ 前端頁面可訪問")
            else:
                logger.error(f"    ❌ 前端頁面不可訪問")
                return False
            
            logger.info(f"  🎉 端到端工作流程測試通過！")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ 端到端測試異常: {e}")
            return False
    
    def run_complete_test(self):
        """執行完整系統測試"""
        logger.info(f"🚀 開始完整系統測試...")
        logger.info(f"=" * 60)
        
        start_time = time.time()
        
        # 1. 測試所有服務健康狀況
        logger.info(f"\n📊 階段1: 服務健康檢查")
        health_results = {}
        
        for service_name, url in self.base_urls.items():
            health_results[service_name] = self.test_service_health(service_name, url)
        
        # 2. 測試題庫API
        logger.info(f"\n📊 階段2: 題庫API測試")
        api_result = self.test_question_bank_api()
        
        # 3. 測試圖片API
        logger.info(f"\n📊 階段3: 圖片API測試")
        image_result = self.test_image_api()
        
        # 4. 測試前端頁面
        logger.info(f"\n📊 階段4: 前端頁面測試")
        frontend_result = self.test_frontend_pages()
        
        # 5. 測試端到端工作流程
        logger.info(f"\n📊 階段5: 端到端工作流程測試")
        e2e_result = self.test_end_to_end_workflow()
        
        # 計算總耗時
        elapsed_time = time.time() - start_time
        
        # 生成測試報告
        self.generate_test_report(health_results, api_result, image_result, frontend_result, e2e_result, elapsed_time)
        
        return all([
            all(health_results.values()),
            api_result,
            image_result, 
            frontend_result,
            e2e_result
        ])
    
    def generate_test_report(self, health_results, api_result, image_result, frontend_result, e2e_result, elapsed_time):
        """生成測試報告"""
        logger.info(f"\n" + "=" * 60)
        logger.info(f"📊 完整系統測試報告")
        logger.info(f"=" * 60)
        
        # 服務健康狀況
        logger.info(f"\n🏥 服務健康狀況:")
        for service, status in health_results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"  {status_icon} {service}")
        
        # 功能測試結果
        logger.info(f"\n🧪 功能測試結果:")
        tests = [
            ("題庫API", api_result),
            ("圖片API", image_result), 
            ("前端頁面", frontend_result),
            ("端到端工作流程", e2e_result)
        ]
        
        for test_name, result in tests:
            status_icon = "✅" if result else "❌"
            logger.info(f"  {status_icon} {test_name}")
        
        # 總結
        total_services = len(health_results)
        healthy_services = sum(health_results.values())
        total_tests = len(tests)
        passed_tests = sum(result for _, result in tests)
        
        logger.info(f"\n📈 測試統計:")
        logger.info(f"  服務健康: {healthy_services}/{total_services}")
        logger.info(f"  功能測試: {passed_tests}/{total_tests}")
        logger.info(f"  總耗時: {elapsed_time:.2f} 秒")
        
        # 最終結果
        all_passed = healthy_services == total_services and passed_tests == total_tests
        
        if all_passed:
            logger.info(f"\n🎉 系統測試全部通過！")
            logger.info(f"✅ InULearning系統已準備就緒，可以正常使用")
        else:
            logger.info(f"\n⚠️  系統測試部分失敗")
            logger.info(f"❌ 需要修復失敗的組件後重新測試")
        
        return all_passed

def main():
    """主程式"""
    tester = SystemTester()
    
    try:
        # 等待服務啟動
        logger.info(f"⏳ 等待服務準備就緒...")
        time.sleep(5)
        
        # 執行完整測試
        success = tester.run_complete_test()
        
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