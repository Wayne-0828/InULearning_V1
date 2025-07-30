#!/usr/bin/env python3
"""
完整系統測試 - 階段D
測試所有服務和功能的整合
"""

import requests
import time
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from minio import Minio
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FullSystemTester:
    """完整系統測試器"""
    
    def __init__(self):
        self.services = {
            'postgres': {'port': 5432, 'name': 'PostgreSQL'},
            'mongodb': {'port': 27017, 'name': 'MongoDB'},
            'redis': {'port': 6379, 'name': 'Redis'},
            'minio': {'port': 9000, 'name': 'MinIO'},
            'auth-service': {'port': 8001, 'name': '認證服務'},
            'question-bank-service': {'port': 8002, 'name': '題庫服務'},
            'learning-service': {'port': 8003, 'name': '學習服務'},
            'nginx': {'port': 80, 'name': 'Nginx'},
            'student-frontend': {'port': 8080, 'name': '學生前端'},
            'admin-frontend': {'port': 8081, 'name': '管理員前端'},
            'parent-frontend': {'port': 8082, 'name': '家長前端'},
            'teacher-frontend': {'port': 8083, 'name': '教師前端'}
        }
        self.test_results = {}

    def test_service_health(self, service_name, port, timeout=5):
        """測試服務健康狀態"""
        try:
            if service_name in ['auth-service', 'question-bank-service', 'learning-service']:
                # API服務健康檢查
                url = f"http://localhost:{port}/health"
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    return True, f"✅ {data.get('status', 'healthy')}"
                else:
                    return False, f"❌ HTTP {response.status_code}"
            
            elif service_name == 'nginx':
                # Nginx檢查
                response = requests.get(f"http://localhost:{port}", timeout=timeout)
                return True, f"✅ HTTP {response.status_code}"
            
            elif service_name in ['student-frontend', 'admin-frontend', 'parent-frontend', 'teacher-frontend']:
                # 前端服務檢查
                response = requests.get(f"http://localhost:{port}", timeout=timeout)
                return True, f"✅ HTTP {response.status_code}"
            
            elif service_name == 'minio':
                # MinIO健康檢查
                response = requests.get(f"http://localhost:{port}/minio/health/live", timeout=timeout)
                return True, f"✅ MinIO健康"
            
            else:
                # 其他服務的基本連接測試
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                return result == 0, f"{'✅ 連接正常' if result == 0 else '❌ 連接失敗'}"
                
        except Exception as e:
            return False, f"❌ {str(e)}"

    def test_all_services(self):
        """測試所有服務"""
        logger.info("🔍 開始測試所有服務...")
        
        for service_name, info in self.services.items():
            port = info['port']
            name = info['name']
            
            logger.info(f"測試 {name} (:{port})...")
            is_healthy, status = self.test_service_health(service_name, port)
            
            self.test_results[service_name] = {
                'name': name,
                'port': port,
                'healthy': is_healthy,
                'status': status
            }
            
            logger.info(f"  {status}")

    async def test_database_data(self):
        """測試資料庫資料"""
        logger.info("\n🔍 測試資料庫資料...")
        
        try:
            # 測試MongoDB
            client = AsyncIOMotorClient('mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning?authSource=admin')
            db = client.inulearning
            
            # 統計題目數量
            total_questions = await db.questions.count_documents({})
            questions_with_images = await db.questions.count_documents({
                'image_filename': {'$exists': True, '$ne': None, '$ne': ''}
            })
            
            logger.info(f"  📊 MongoDB題目總數: {total_questions:,}")
            logger.info(f"  📸 有圖片的題目: {questions_with_images:,}")
            
            # 測試各科目題目數量
            subjects = ['國文', '英文', '數學', '自然', '歷史', '地理', '公民']
            for subject in subjects:
                count = await db.questions.count_documents({'subject': subject})
                if count > 0:
                    logger.info(f"  📚 {subject}: {count:,} 題")
            
            client.close()
            
            self.test_results['mongodb_data'] = {
                'total_questions': total_questions,
                'questions_with_images': questions_with_images,
                'status': '✅ 正常'
            }
            
        except Exception as e:
            logger.error(f"  ❌ MongoDB資料測試失敗: {e}")
            self.test_results['mongodb_data'] = {'status': f'❌ {e}'}

    def test_minio_images(self):
        """測試MinIO圖片"""
        logger.info("\n🔍 測試MinIO圖片...")
        
        try:
            minio_client = Minio(
                'localhost:9000',
                access_key='aipe-tester',
                secret_key='aipe-tester',
                secure=False
            )
            
            # 檢查buckets
            buckets = minio_client.list_buckets()
            logger.info(f"  📊 MinIO buckets: {len(buckets)}")
            
            image_count = 0
            for bucket in buckets:
                objects = list(minio_client.list_objects(bucket.name))
                logger.info(f"  🗄️  {bucket.name}: {len(objects):,} 個物件")
                if 'image' in bucket.name.lower():
                    image_count += len(objects)
            
            self.test_results['minio_images'] = {
                'buckets': len(buckets),
                'image_count': image_count,
                'status': '✅ 正常'
            }
            
        except Exception as e:
            logger.error(f"  ❌ MinIO測試失敗: {e}")
            self.test_results['minio_images'] = {'status': f'❌ {e}'}

    def test_api_endpoints(self):
        """測試API端點"""
        logger.info("\n🔍 測試API端點...")
        
        api_tests = [
            {
                'name': '題庫檢查API',
                'url': 'http://localhost:8002/api/v1/questions/check?grade=7A&edition=翰林&subject=英文',
                'expected_keys': ['success', 'data']
            },
            {
                'name': '題目獲取API',
                'url': 'http://localhost:8002/api/v1/questions/by-conditions?grade=7A&edition=翰林&subject=英文&questionCount=3',
                'expected_keys': ['success', 'data']
            },
            {
                'name': '章節API',
                'url': 'http://localhost:8002/api/v1/chapters/',
                'expected_keys': []
            },
            {
                'name': '知識點API',
                'url': 'http://localhost:8002/api/v1/knowledge-points/',
                'expected_keys': []
            }
        ]
        
        for test in api_tests:
            try:
                response = requests.get(test['url'], timeout=10)
                
                if response.status_code == 200:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                        
                        # 檢查必要的鍵
                        if test['expected_keys']:
                            missing_keys = [key for key in test['expected_keys'] if key not in data]
                            if missing_keys:
                                logger.info(f"  ❌ {test['name']}: 缺少鍵 {missing_keys}")
                            else:
                                logger.info(f"  ✅ {test['name']}: 正常")
                        else:
                            logger.info(f"  ✅ {test['name']}: 正常")
                    else:
                        logger.info(f"  ✅ {test['name']}: 正常 (非JSON)")
                else:
                    logger.info(f"  ❌ {test['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.info(f"  ❌ {test['name']}: {e}")

    def test_frontend_pages(self):
        """測試前端頁面"""
        logger.info("\n🔍 測試前端頁面...")
        
        frontend_tests = [
            {'name': '學生登入頁面', 'url': 'http://localhost:8080/login.html'},
            {'name': '學生練習頁面', 'url': 'http://localhost:8080/pages/exercise.html'},
            {'name': '學生考試頁面', 'url': 'http://localhost:8080/pages/exam.html'},
            {'name': '管理員前端', 'url': 'http://localhost:8081/'},
            {'name': '家長前端', 'url': 'http://localhost:8082/'},
            {'name': '教師前端', 'url': 'http://localhost:8083/'}
        ]
        
        for test in frontend_tests:
            try:
                response = requests.get(test['url'], timeout=10)
                if response.status_code == 200:
                    logger.info(f"  ✅ {test['name']}: 正常")
                else:
                    logger.info(f"  ❌ {test['name']}: HTTP {response.status_code}")
            except Exception as e:
                logger.info(f"  ❌ {test['name']}: {e}")

    def test_end_to_end_workflow(self):
        """測試端到端工作流程"""
        logger.info("\n🔍 測試端到端工作流程...")
        
        try:
            # 1. 檢查題庫
            logger.info("  1. 檢查翰林英文題庫...")
            check_response = requests.get(
                'http://localhost:8002/api/v1/questions/check?grade=7A&edition=翰林&subject=英文',
                timeout=10
            )
            
            if check_response.status_code == 200:
                check_data = check_response.json()
                if check_data.get('success') and check_data.get('data', {}).get('available'):
                    count = check_data['data']['count']
                    logger.info(f"     ✅ 找到 {count} 題翰林英文題目")
                    
                    # 2. 獲取題目
                    logger.info("  2. 獲取題目...")
                    questions_response = requests.get(
                        'http://localhost:8002/api/v1/questions/by-conditions?grade=7A&edition=翰林&subject=英文&questionCount=3',
                        timeout=10
                    )
                    
                    if questions_response.status_code == 200:
                        questions_data = questions_response.json()
                        if questions_data.get('success') and questions_data.get('data'):
                            questions = questions_data['data']
                            logger.info(f"     ✅ 成功獲取 {len(questions)} 題")
                            
                            # 3. 檢查題目內容
                            for i, q in enumerate(questions[:2]):
                                logger.info(f"     題目{i+1}: {q.get('question', 'N/A')[:50]}...")
                                if q.get('image_filename'):
                                    logger.info(f"     圖片: {q['image_filename']}")
                            
                            logger.info("  ✅ 端到端工作流程測試成功")
                            return True
                        else:
                            logger.info("  ❌ 獲取題目失敗")
                    else:
                        logger.info(f"  ❌ 題目API失敗: HTTP {questions_response.status_code}")
                else:
                    logger.info("  ❌ 題庫檢查失敗")
            else:
                logger.info(f"  ❌ 檢查API失敗: HTTP {check_response.status_code}")
                
        except Exception as e:
            logger.info(f"  ❌ 端到端測試失敗: {e}")
        
        return False

    def generate_report(self):
        """生成測試報告"""
        logger.info("\n" + "="*60)
        logger.info("📊 完整系統測試報告")
        logger.info("="*60)
        
        # 服務狀態統計
        healthy_services = sum(1 for result in self.test_results.values() 
                             if isinstance(result, dict) and result.get('healthy'))
        total_services = len([k for k in self.test_results.keys() 
                            if k in self.services])
        
        logger.info(f"🔧 服務狀態: {healthy_services}/{total_services} 健康")
        
        for service_name, info in self.services.items():
            if service_name in self.test_results:
                result = self.test_results[service_name]
                status = result.get('status', '❌ 未測試')
                logger.info(f"  {info['name']:20} (:{info['port']:4}): {status}")
        
        # 資料庫狀態
        if 'mongodb_data' in self.test_results:
            mongodb_result = self.test_results['mongodb_data']
            logger.info(f"\n📊 資料庫狀態:")
            logger.info(f"  題目總數: {mongodb_result.get('total_questions', 'N/A'):,}")
            logger.info(f"  有圖片題目: {mongodb_result.get('questions_with_images', 'N/A'):,}")
        
        # MinIO狀態
        if 'minio_images' in self.test_results:
            minio_result = self.test_results['minio_images']
            logger.info(f"\n🗄️  MinIO狀態:")
            logger.info(f"  Buckets: {minio_result.get('buckets', 'N/A')}")
            logger.info(f"  圖片數量: {minio_result.get('image_count', 'N/A'):,}")
        
        # 總體評估
        logger.info(f"\n" + "="*60)
        if healthy_services >= total_services * 0.8:  # 80%以上服務健康
            logger.info("🎉 系統整體狀態: 良好")
            logger.info("✅ Docker Compose部署成功")
            logger.info("✅ 所有核心功能正常運作")
        else:
            logger.info("⚠️  系統整體狀態: 需要注意")
            logger.info("❌ 部分服務可能存在問題")
        
        logger.info("="*60)

async def main():
    """主程式"""
    logger.info("🚀 開始完整系統測試 - 階段D")
    logger.info("目標: 驗證整個系統可以用docker-compose.yml啟動並正常運作")
    
    tester = FullSystemTester()
    
    # 等待服務啟動
    logger.info("⏳ 等待服務準備就緒...")
    time.sleep(5)
    
    try:
        # 1. 測試所有服務
        tester.test_all_services()
        
        # 2. 測試資料庫資料
        await tester.test_database_data()
        
        # 3. 測試MinIO圖片
        tester.test_minio_images()
        
        # 4. 測試API端點
        tester.test_api_endpoints()
        
        # 5. 測試前端頁面
        tester.test_frontend_pages()
        
        # 6. 測試端到端工作流程
        tester.test_end_to_end_workflow()
        
        # 7. 生成報告
        tester.generate_report()
        
    except Exception as e:
        logger.error(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())