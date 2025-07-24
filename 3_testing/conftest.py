"""
pytest 配置檔案
包含共用的 fixtures 和測試設定
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

# 測試配置
pytest_plugins = [
    "pytest_asyncio",
    "pytest_mock",
]

# 測試標記
def pytest_configure(config):
    """配置 pytest 標記"""
    config.addinivalue_line(
        "markers", "unit: 標記為單元測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記為整合測試"
    )
    config.addinivalue_line(
        "markers", "e2e: 標記為端到端測試"
    )
    config.addinivalue_line(
        "markers", "performance: 標記為效能測試"
    )
    config.addinivalue_line(
        "markers", "slow: 標記為慢速測試"
    )

# 測試資料夾設定
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """測試資料目錄"""
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def test_reports_dir() -> Path:
    """測試報告目錄"""
    reports_dir = Path(__file__).parent / "test_reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

# 環境變數 fixtures
@pytest.fixture(scope="session")
def test_env_vars() -> Dict[str, str]:
    """測試環境變數"""
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://aipe-tester:aipe-tester@localhost:5432/inulearning"),
        "MONGODB_URL": os.getenv("MONGODB_URL", "mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning"),
        "REDIS_URL": os.getenv("REDIS_URL", "redis://:redis_password@localhost:6379/1"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "test-secret-key"),
        "AUTH_SERVICE_URL": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
        "LEARNING_SERVICE_URL": os.getenv("LEARNING_SERVICE_URL", "http://localhost:8002"),
        "QUESTION_BANK_SERVICE_URL": os.getenv("QUESTION_BANK_SERVICE_URL", "http://localhost:8003"),
        "AI_ANALYSIS_SERVICE_URL": os.getenv("AI_ANALYSIS_SERVICE_URL", "http://localhost:8004"),
        "TEST_MODE": "true",
        "LOG_LEVEL": "INFO"
    }

# 服務端口配置
@pytest.fixture(scope="session")
def service_ports() -> Dict[str, int]:
    """服務端口配置"""
    return {
        "auth_service": 8001,
        "learning_service": 8002,
        "question_bank_service": 8003,
        "ai_analysis_service": 8004,
        "api_gateway": 8000
    }

# 資料庫配置
@pytest.fixture(scope="session")
def database_config() -> Dict[str, Any]:
    """資料庫配置"""
    return {
        "postgresql": {
            "host": "localhost",
            "port": 5432,
            "database": "inulearning",
            "user": "aipe-tester",
            "password": "aipe-tester"
        },
        "mongodb": {
            "host": "localhost",
            "port": 27017,
            "database": "inulearning",
            "username": "aipe-tester",
            "password": "aipe-tester"
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 1,
            "password": "redis_password"
        }
    }

# 測試用戶資料
@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """測試用戶資料"""
    return {
        "student": {
            "email": "student@example.com",
            "username": "teststudent",
            "password": "studentpass123",
            "first_name": "Test",
            "last_name": "Student",
            "role": "student",
            "grade": "7A",
            "school": "測試中學"
        },
        "teacher": {
            "email": "teacher@example.com",
            "username": "testteacher",
            "password": "teacherpass123",
            "first_name": "Test",
            "last_name": "Teacher",
            "role": "teacher",
            "subject": "數學",
            "school": "測試中學"
        },
        "parent": {
            "email": "parent@example.com",
            "username": "testparent",
            "password": "parentpass123",
            "first_name": "Test",
            "last_name": "Parent",
            "role": "parent",
            "school": "測試中學"
        }
    }

@pytest.fixture
def test_teacher_data() -> Dict[str, Any]:
    """測試教師資料"""
    return {
        "email": "teacher@example.com",
        "username": "testteacher",
        "password": "teacherpass123",
        "first_name": "Test",
        "last_name": "Teacher",
        "role": "teacher",
        "subject": "數學",
        "school": "測試中學"
    }

# 測試題目資料
@pytest.fixture
def test_question_data() -> Dict[str, Any]:
    """測試題目資料"""
    return {
        "math_question": {
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "chapter": "1-1 一元一次方程式",
            "topic": "一元一次方程式",
            "knowledge_point": ["方程式求解"],
            "difficulty": "normal",
            "question": "解下列方程式：2x + 5 = 13",
            "options": {
                "A": "x = 4",
                "B": "x = 6",
                "C": "x = 8",
                "D": "x = 10"
            },
            "answer": "A",
            "explanation": "解一元一次方程式 2x + 5 = 13，首先將 5 移到等式右邊得到 2x = 13 - 5 = 8，再將兩邊同除以 2 得到 x = 4，因此正確答案是選項 A。"
        },
        "english_question": {
            "grade": "7A",
            "subject": "英文",
            "publisher": "南一",
            "chapter": "1-1 基礎文法",
            "topic": "be 動詞",
            "knowledge_point": ["be 動詞用法"],
            "difficulty": "easy",
            "question": "選擇正確的 be 動詞：She ___ a student.",
            "options": {
                "A": "am",
                "B": "is",
                "C": "are",
                "D": "be"
            },
            "answer": "B",
            "explanation": "第三人稱單數主詞 She 搭配 be 動詞 is。"
        }
    }

# 測試學習會話資料
@pytest.fixture
def test_learning_session_data() -> Dict[str, Any]:
    """測試學習會話資料"""
    return {
        "math_session": {
            "user_id": "test_user_123",
            "grade": "7A",
            "subject": "數學",
            "publisher": "南一",
            "chapter": "第一章",
            "difficulty": "normal",
            "question_count": 5,
            "knowledge_points": ["基礎運算", "代數概念"]
        },
        "english_session": {
            "user_id": "test_user_123",
            "grade": "7A",
            "subject": "英文",
            "publisher": "南一",
            "chapter": "第一章",
            "difficulty": "easy",
            "question_count": 3,
            "knowledge_points": ["基礎文法", "詞彙"]
        }
    }

# Mock 資料庫會話
@pytest.fixture
def mock_db_session():
    """Mock 資料庫會話"""
    mock_session = Mock()
    mock_session.commit = Mock()
    mock_session.rollback = Mock()
    mock_session.close = Mock()
    return mock_session

# Mock Redis 客戶端
@pytest.fixture
def mock_redis_client():
    """Mock Redis 客戶端"""
    mock_redis = Mock()
    mock_redis.get = Mock(return_value=None)
    mock_redis.set = Mock(return_value=True)
    mock_redis.delete = Mock(return_value=1)
    mock_redis.exists = Mock(return_value=False)
    return mock_redis

# Mock MongoDB 客戶端
@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB 客戶端"""
    mock_mongo = Mock()
    mock_collection = Mock()
    mock_collection.find_one = Mock(return_value=None)
    mock_collection.find = Mock(return_value=[])
    mock_collection.insert_one = Mock(return_value=Mock(inserted_id="test_id"))
    mock_collection.update_one = Mock(return_value=Mock(modified_count=1))
    mock_collection.delete_one = Mock(return_value=Mock(deleted_count=1))
    mock_mongo.test_collection = mock_collection
    return mock_mongo

# 測試 HTTP 客戶端
@pytest.fixture
def test_http_client():
    """測試 HTTP 客戶端"""
    import httpx
    return httpx.AsyncClient(timeout=30.0)

# 服務健康檢查
@pytest.fixture(scope="session")
def check_services_health(service_ports) -> bool:
    """檢查服務健康狀態"""
    import requests
    import time
    
    def check_service(service_name: str, port: int) -> bool:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    # 等待服務啟動
    time.sleep(2)
    
    health_status = {}
    for service_name, port in service_ports.items():
        health_status[service_name] = check_service(service_name, port)
    
    # 記錄健康狀態
    print(f"\n🔍 服務健康檢查結果:")
    for service_name, is_healthy in health_status.items():
        status = "✅ 正常" if is_healthy else "❌ 異常"
        print(f"  {service_name}: {status}")
    
    return health_status

# 測試資料庫連接
@pytest.fixture(scope="session")
def test_database_connections(database_config) -> Dict[str, bool]:
    """測試資料庫連接"""
    import psycopg2
    import pymongo
    import redis
    
    connection_status = {}
    
    # 測試 PostgreSQL
    try:
        conn = psycopg2.connect(
            host=database_config["postgresql"]["host"],
            port=database_config["postgresql"]["port"],
            database=database_config["postgresql"]["database"],
            user=database_config["postgresql"]["user"],
            password=database_config["postgresql"]["password"]
        )
        conn.close()
        connection_status["postgresql"] = True
    except Exception as e:
        print(f"❌ PostgreSQL 連接失敗: {e}")
        connection_status["postgresql"] = False
    
    # 測試 MongoDB
    try:
        client = pymongo.MongoClient(
            f"mongodb://{database_config['mongodb']['host']}:{database_config['mongodb']['port']}"
        )
        client.admin.command('ping')
        client.close()
        connection_status["mongodb"] = True
    except Exception as e:
        print(f"❌ MongoDB 連接失敗: {e}")
        connection_status["mongodb"] = False
    
    # 測試 Redis
    try:
        r = redis.Redis(
            host=database_config["redis"]["host"],
            port=database_config["redis"]["port"],
            db=database_config["redis"]["db"]
        )
        r.ping()
        r.close()
        connection_status["redis"] = True
    except Exception as e:
        print(f"❌ Redis 連接失敗: {e}")
        connection_status["redis"] = False
    
    print(f"\n🗄️ 資料庫連接測試結果:")
    for db_name, is_connected in connection_status.items():
        status = "✅ 連接成功" if is_connected else "❌ 連接失敗"
        print(f"  {db_name}: {status}")
    
    return connection_status

# 測試環境設定
@pytest.fixture(autouse=True)
def setup_test_environment(test_env_vars):
    """設定測試環境"""
    # 設定環境變數
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    yield
    
    # 清理環境變數
    for key in test_env_vars.keys():
        if key in os.environ:
            del os.environ[key]

# 日誌配置
@pytest.fixture(scope="session")
def setup_logging():
    """設定測試日誌"""
    import logging
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_reports/test.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# 測試執行器配置
def pytest_collection_modifyitems(config, items):
    """修改測試收集項目"""
    # 為慢速測試添加標記
    for item in items:
        if "performance" in item.nodeid or "e2e" in item.nodeid:
            item.add_marker(pytest.mark.slow)

# 測試報告配置
def pytest_html_report_title(report):
    """設定 HTML 報告標題"""
    report.title = "InULearning_V1 測試報告"

# 測試結果處理
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """處理測試結果"""
    if call.when == "call":
        # 添加測試描述
        if hasattr(item._obj, '__doc__') and item._obj.__doc__ is None:
            item._obj.__doc__ = "無描述"
        call.excinfo = None 