"""
測試輔助函數模組
提供測試過程中常用的工具函數
"""

import os
import sys
import time
import json
import logging
import requests
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from unittest.mock import Mock, patch
import psycopg2
import pymongo
import redis
from faker import Faker
from dataclasses import dataclass

# 設定 Faker 為中文
fake = Faker(['zh_TW'])

@dataclass
class TestResult:
    """測試結果資料類別"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TestHelpers:
    """測試輔助工具類別"""
    
    @staticmethod
    def log_test_result(test_name: str, result: TestResult):
        """記錄測試結果"""
        if result.success:
            logging.info(f"✅ {test_name}: {result.message}")
        else:
            logging.error(f"❌ {test_name}: {result.message}")
            if result.error:
                logging.error(f"   錯誤詳情: {result.error}")
    


class TestHelper:
    """測試輔助類別"""
    
    @staticmethod
    def retry_request(func, max_retries: int = 3, delay: float = 1.0):
        """重試請求函數"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (attempt + 1))
    
    @staticmethod
    def validate_response(response: requests.Response, expected_status: int = 200) -> TestResult:
        """驗證 API 回應"""
        try:
            if response.status_code != expected_status:
                return TestResult(
                    success=False, 
                    message="API 回應狀態碼錯誤", 
                    error=f"狀態碼: {response.status_code}, 預期: {expected_status}"
                )
            
            data = response.json()
            return TestResult(success=True, message="API 回應驗證成功", data=data)
        except json.JSONDecodeError:
            return TestResult(
                success=False, 
                message="API 回應格式錯誤", 
                error="回應不是有效的 JSON 格式"
            )
        except Exception as e:
            return TestResult(
                success=False, 
                message="API 回應驗證失敗", 
                error=str(e)
            )
    
    @staticmethod
    def generate_test_data(data_type: str) -> Dict[str, Any]:
        """生成測試資料"""
        if data_type == "user":
            return {
                "email": fake.email(),
                "username": fake.user_name(),
                "password": fake.password(length=12),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "role": fake.random_element(["student", "teacher", "parent"]),
                "grade": fake.random_element(["7A", "7B", "8A", "8B", "9A", "9B"]),
                "school": fake.company()
            }
        elif data_type == "question":
            return {
                "grade": fake.random_element(["7A", "7B", "8A", "8B"]),
                "subject": fake.random_element(["數學", "英文", "國文", "自然"]),
                "publisher": fake.random_element(["南一", "康軒", "翰林"]),
                "chapter": f"{fake.random_int(1, 10)}-{fake.random_int(1, 5)} {fake.word()}",
                "topic": fake.sentence(nb_words=3),
                "knowledge_point": [fake.word() for _ in range(fake.random_int(1, 3))],
                "difficulty": fake.random_element(["easy", "normal", "hard"]),
                "question": fake.sentence(nb_words=10),
                "options": {
                    "A": fake.sentence(nb_words=5),
                    "B": fake.sentence(nb_words=5),
                    "C": fake.sentence(nb_words=5),
                    "D": fake.sentence(nb_words=5)
                },
                "answer": fake.random_element(["A", "B", "C", "D"]),
                "explanation": fake.text(max_nb_chars=200)
            }
        elif data_type == "learning_session":
            return {
                "user_id": fake.random_int(1, 1000),
                "grade": fake.random_element(["7A", "7B", "8A", "8B"]),
                "subject": fake.random_element(["數學", "英文", "國文"]),
                "publisher": fake.random_element(["南一", "康軒", "翰林"]),
                "chapter": f"第{fake.random_int(1, 10)}章",
                "difficulty": fake.random_element(["easy", "normal", "hard"]),
                "question_count": fake.random_int(5, 20),
                "knowledge_points": [fake.word() for _ in range(fake.random_int(2, 5))]
            }
        else:
            raise ValueError(f"不支援的資料類型: {data_type}")
    
    @staticmethod
    def log_test_result(test_name: str, success: bool, details: str = ""):
        """記錄測試結果"""
        status = "✅ 通過" if success else "❌ 失敗"
        logging.info(f"{test_name}: {status}")
        if details:
            logging.info(f"  詳細資訊: {details}")
    
    @staticmethod
    def cleanup_test_data():
        """清理測試資料"""
        # 這裡可以實現清理測試資料的邏輯
        pass

class DatabaseHelper:
    """資料庫測試輔助類別"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def test_postgresql_connection(self) -> bool:
        """測試 PostgreSQL 連接"""
        try:
            conn = psycopg2.connect(
                host=self.config["postgresql"]["host"],
                port=self.config["postgresql"]["port"],
                database=self.config["postgresql"]["database"],
                user=self.config["postgresql"]["user"],
                password=self.config["postgresql"]["password"]
            )
            conn.close()
            self.logger.info("✅ PostgreSQL 連接成功")
            return True
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL 連接失敗: {e}")
            return False
    
    def test_mongodb_connection(self) -> bool:
        """測試 MongoDB 連接"""
        try:
            client = pymongo.MongoClient(
                f"mongodb://{self.config['mongodb']['host']}:{self.config['mongodb']['port']}"
            )
            client.admin.command('ping')
            client.close()
            self.logger.info("✅ MongoDB 連接成功")
            return True
        except Exception as e:
            self.logger.error(f"❌ MongoDB 連接失敗: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """測試 Redis 連接"""
        try:
            r = redis.Redis(
                host=self.config["redis"]["host"],
                port=self.config["redis"]["port"],
                db=self.config["redis"]["db"]
            )
            r.ping()
            r.close()
            self.logger.info("✅ Redis 連接成功")
            return True
        except Exception as e:
            self.logger.error(f"❌ Redis 連接失敗: {e}")
            return False
    
    def test_all_connections(self) -> Dict[str, bool]:
        """測試所有資料庫連接"""
        results = {
            "postgresql": self.test_postgresql_connection(),
            "mongodb": self.test_mongodb_connection(),
            "redis": self.test_redis_connection()
        }
        
        self.logger.info("🗄️ 資料庫連接測試結果:")
        for db_name, is_connected in results.items():
            status = "✅ 連接成功" if is_connected else "❌ 連接失敗"
            self.logger.info(f"  {db_name}: {status}")
        
        return results

class APITestHelper:
    """API 測試輔助類別"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def check_service_health(self, service_name: str, port: int) -> bool:
        """檢查服務健康狀態"""
        try:
            response = self.session.get(
                f"http://localhost:{port}/health",
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info(f"✅ {service_name} 健康檢查通過")
                return True
            else:
                self.logger.warning(f"⚠️ {service_name} 健康檢查失敗: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ {service_name} 健康檢查異常: {e}")
            return False
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"❌ 請求失敗: {e}")
            raise
    
    def validate_api_response(self, response: requests.Response, expected_status: int = 200) -> Dict[str, Any]:
        """驗證 API 回應並返回資料"""
        if response.status_code != expected_status:
            raise ValueError(f"API 回應狀態碼錯誤: {response.status_code}, 預期: {expected_status}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            raise ValueError("API 回應不是有效的 JSON 格式")
    
    def wait_for_service(self, service_name: str, port: int, max_wait: int = 60) -> bool:
        """等待服務啟動"""
        self.logger.info(f"⏳ 等待 {service_name} 服務啟動...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_service_health(service_name, port):
                return True
            time.sleep(2)
        
        self.logger.error(f"❌ {service_name} 服務啟動超時")
        return False
    
    def cleanup(self):
        """清理資源"""
        self.session.close()

# 全域測試輔助實例
test_helper = TestHelper() 