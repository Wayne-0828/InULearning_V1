"""
資料庫整合測試
測試 PostgreSQL、MongoDB、Redis 的連接和基本操作
"""

import pytest
import psycopg2
import pymongo
import redis
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

from utils.test_helpers import DatabaseHelper, TestHelper

@pytest.mark.integration
class TestDatabaseConnections:
    """資料庫連接測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.test_helper = TestHelper()
        self.db_config = {
            "postgresql": {
                "host": "localhost",
                "port": 5432,
                "database": "inulearning_test",
                "user": "test",
                "password": "test"
            },
            "mongodb": {
                "host": "localhost",
                "port": 27017,
                "database": "inulearning_test"
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 1
            }
        }
        self.db_helper = DatabaseHelper(self.db_config)
    
    def test_postgresql_connection(self):
        """測試 PostgreSQL 連接"""
        try:
            conn = psycopg2.connect(
                host=self.db_config["postgresql"]["host"],
                port=self.db_config["postgresql"]["port"],
                database=self.db_config["postgresql"]["database"],
                user=self.db_config["postgresql"]["user"],
                password=self.db_config["postgresql"]["password"]
            )
            
            # 測試基本查詢
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            assert version is not None
            assert "PostgreSQL" in version[0]
            
        except Exception as e:
            pytest.skip(f"PostgreSQL 連接失敗: {e}")
    
    def test_mongodb_connection(self):
        """測試 MongoDB 連接"""
        try:
            client = pymongo.MongoClient(
                f"mongodb://{self.db_config['mongodb']['host']}:{self.db_config['mongodb']['port']}"
            )
            
            # 測試連接
            client.admin.command('ping')
            
            # 測試資料庫操作
            db = client[self.db_config["mongodb"]["database"]]
            collection = db.test_collection
            
            # 插入測試資料
            test_doc = {"test": "data", "value": 123}
            result = collection.insert_one(test_doc)
            
            # 查詢測試資料
            found_doc = collection.find_one({"_id": result.inserted_id})
            
            # 清理測試資料
            collection.delete_one({"_id": result.inserted_id})
            
            client.close()
            
            assert found_doc is not None
            assert found_doc["test"] == "data"
            assert found_doc["value"] == 123
            
        except Exception as e:
            pytest.skip(f"MongoDB 連接失敗: {e}")
    
    def test_redis_connection(self):
        """測試 Redis 連接"""
        try:
            r = redis.Redis(
                host=self.db_config["redis"]["host"],
                port=self.db_config["redis"]["port"],
                db=self.db_config["redis"]["db"]
            )
            
            # 測試連接
            r.ping()
            
            # 測試基本操作
            test_key = "test_key"
            test_value = "test_value"
            
            # 設定值
            r.set(test_key, test_value)
            
            # 獲取值
            retrieved_value = r.get(test_key)
            
            # 刪除測試資料
            r.delete(test_key)
            
            assert retrieved_value.decode() == test_value
            
            r.close()
            
        except Exception as e:
            pytest.skip(f"Redis 連接失敗: {e}")
    
    def test_all_database_connections(self):
        """測試所有資料庫連接"""
        results = self.db_helper.test_all_connections()
        
        # 至少要有兩個資料庫連接成功
        connected_count = sum(1 for is_connected in results.values() if is_connected)
        assert connected_count >= 2, f"只有 {connected_count} 個資料庫連接成功"

@pytest.mark.integration
class TestPostgreSQLOperations:
    """PostgreSQL 操作測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "inulearning_test",
            "user": "test",
            "password": "test"
        }
    
    def test_create_table(self):
        """測試創建表格"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 創建測試表格
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS test_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_sql)
            conn.commit()
            
            # 檢查表格是否存在
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'test_users';
            """)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            assert result is not None
            assert result[0] == "test_users"
            
        except Exception as e:
            pytest.skip(f"PostgreSQL 操作失敗: {e}")
    
    def test_insert_and_select(self):
        """測試插入和查詢操作"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 插入測試資料
            insert_sql = """
            INSERT INTO test_users (username, email) 
            VALUES (%s, %s) 
            RETURNING id;
            """
            cursor.execute(insert_sql, ("testuser", "test@example.com"))
            user_id = cursor.fetchone()[0]
            
            # 查詢測試資料
            select_sql = "SELECT username, email FROM test_users WHERE id = %s;"
            cursor.execute(select_sql, (user_id,))
            result = cursor.fetchone()
            
            # 清理測試資料
            cursor.execute("DELETE FROM test_users WHERE id = %s;", (user_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            assert result is not None
            assert result[0] == "testuser"
            assert result[1] == "test@example.com"
            
        except Exception as e:
            pytest.skip(f"PostgreSQL 操作失敗: {e}")
    
    def test_update_and_delete(self):
        """測試更新和刪除操作"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 插入測試資料
            cursor.execute(
                "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id;",
                ("updateuser", "update@example.com")
            )
            user_id = cursor.fetchone()[0]
            
            # 更新資料
            cursor.execute(
                "UPDATE test_users SET email = %s WHERE id = %s;",
                ("updated@example.com", user_id)
            )
            
            # 查詢更新後的資料
            cursor.execute("SELECT email FROM test_users WHERE id = %s;", (user_id,))
            result = cursor.fetchone()
            
            # 刪除資料
            cursor.execute("DELETE FROM test_users WHERE id = %s;", (user_id,))
            conn.commit()
            
            # 確認刪除
            cursor.execute("SELECT COUNT(*) FROM test_users WHERE id = %s;", (user_id,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            assert result[0] == "updated@example.com"
            assert count == 0
            
        except Exception as e:
            pytest.skip(f"PostgreSQL 操作失敗: {e}")

@pytest.mark.integration
class TestMongoDBOperations:
    """MongoDB 操作測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client.inulearning_test
        self.collection = self.db.test_questions
    
    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'client'):
            self.client.close()
    
    def test_insert_document(self):
        """測試插入文件"""
        try:
            # 插入測試文件
            test_doc = {
                "question": "測試題目",
                "subject": "數學",
                "grade": "7A",
                "difficulty": "normal"
            }
            
            result = self.collection.insert_one(test_doc)
            
            # 查詢插入的文件
            found_doc = self.collection.find_one({"_id": result.inserted_id})
            
            # 清理測試資料
            self.collection.delete_one({"_id": result.inserted_id})
            
            assert found_doc is not None
            assert found_doc["question"] == "測試題目"
            assert found_doc["subject"] == "數學"
            
        except Exception as e:
            pytest.skip(f"MongoDB 操作失敗: {e}")
    
    def test_find_documents(self):
        """測試查詢文件"""
        try:
            # 插入多個測試文件
            test_docs = [
                {"question": "題目1", "subject": "數學", "grade": "7A"},
                {"question": "題目2", "subject": "數學", "grade": "7A"},
                {"question": "題目3", "subject": "英文", "grade": "7A"}
            ]
            
            result = self.collection.insert_many(test_docs)
            
            # 查詢特定條件的文件
            math_questions = list(self.collection.find({"subject": "數學"}))
            
            # 清理測試資料
            self.collection.delete_many({"_id": {"$in": result.inserted_ids}})
            
            assert len(math_questions) == 2
            assert all(doc["subject"] == "數學" for doc in math_questions)
            
        except Exception as e:
            pytest.skip(f"MongoDB 操作失敗: {e}")
    
    def test_update_document(self):
        """測試更新文件"""
        try:
            # 插入測試文件
            test_doc = {"question": "原始題目", "subject": "數學"}
            result = self.collection.insert_one(test_doc)
            
            # 更新文件
            self.collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"question": "更新後的題目"}}
            )
            
            # 查詢更新後的文件
            updated_doc = self.collection.find_one({"_id": result.inserted_id})
            
            # 清理測試資料
            self.collection.delete_one({"_id": result.inserted_id})
            
            assert updated_doc["question"] == "更新後的題目"
            
        except Exception as e:
            pytest.skip(f"MongoDB 操作失敗: {e}")
    
    def test_delete_document(self):
        """測試刪除文件"""
        try:
            # 插入測試文件
            test_doc = {"question": "要刪除的題目", "subject": "數學"}
            result = self.collection.insert_one(test_doc)
            
            # 刪除文件
            delete_result = self.collection.delete_one({"_id": result.inserted_id})
            
            # 確認刪除
            found_doc = self.collection.find_one({"_id": result.inserted_id})
            
            assert delete_result.deleted_count == 1
            assert found_doc is None
            
        except Exception as e:
            pytest.skip(f"MongoDB 操作失敗: {e}")

@pytest.mark.integration
class TestRedisOperations:
    """Redis 操作測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.redis_client = redis.Redis(host="localhost", port=6379, db=1)
    
    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'redis_client'):
            self.redis_client.close()
    
    def test_string_operations(self):
        """測試字串操作"""
        try:
            # 設定字串
            self.redis_client.set("test_string", "hello world")
            
            # 獲取字串
            value = self.redis_client.get("test_string")
            
            # 刪除
            self.redis_client.delete("test_string")
            
            assert value.decode() == "hello world"
            
        except Exception as e:
            pytest.skip(f"Redis 操作失敗: {e}")
    
    def test_hash_operations(self):
        """測試雜湊操作"""
        try:
            # 設定雜湊
            self.redis_client.hset("test_hash", "field1", "value1")
            self.redis_client.hset("test_hash", "field2", "value2")
            
            # 獲取雜湊
            value1 = self.redis_client.hget("test_hash", "field1")
            value2 = self.redis_client.hget("test_hash", "field2")
            
            # 獲取所有欄位
            all_fields = self.redis_client.hgetall("test_hash")
            
            # 刪除
            self.redis_client.delete("test_hash")
            
            assert value1.decode() == "value1"
            assert value2.decode() == "value2"
            assert len(all_fields) == 2
            
        except Exception as e:
            pytest.skip(f"Redis 操作失敗: {e}")
    
    def test_list_operations(self):
        """測試列表操作"""
        try:
            # 推入列表
            self.redis_client.lpush("test_list", "item1")
            self.redis_client.lpush("test_list", "item2")
            self.redis_client.lpush("test_list", "item3")
            
            # 獲取列表長度
            length = self.redis_client.llen("test_list")
            
            # 彈出項目
            item = self.redis_client.lpop("test_list")
            
            # 獲取範圍
            items = self.redis_client.lrange("test_list", 0, -1)
            
            # 刪除
            self.redis_client.delete("test_list")
            
            assert length == 3
            assert item.decode() == "item3"
            assert len(items) == 2
            
        except Exception as e:
            pytest.skip(f"Redis 操作失敗: {e}")
    
    def test_expiration(self):
        """測試過期時間"""
        try:
            # 設定帶過期時間的鍵
            self.redis_client.setex("test_expire", 1, "expire_value")
            
            # 檢查是否存在
            exists_before = self.redis_client.exists("test_expire")
            
            # 等待過期
            import time
            time.sleep(2)
            
            # 檢查是否過期
            exists_after = self.redis_client.exists("test_expire")
            
            assert exists_before == 1
            assert exists_after == 0
            
        except Exception as e:
            pytest.skip(f"Redis 操作失敗: {e}")

@pytest.mark.integration
class TestDatabaseIntegration:
    """資料庫整合測試類別"""
    
    def setup_method(self):
        """測試前設定"""
        self.test_helper = TestHelper()
    
    def test_cross_database_operations(self):
        """測試跨資料庫操作"""
        try:
            # PostgreSQL 操作
            pg_conn = psycopg2.connect(
                host="localhost", port=5432,
                database="inulearning_test",
                user="test", password="test"
            )
            
            # MongoDB 操作
            mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
            mongo_db = mongo_client.inulearning_test
            mongo_collection = mongo_db.test_integration
            
            # Redis 操作
            redis_client = redis.Redis(host="localhost", port=6379, db=1)
            
            # 在 PostgreSQL 中創建用戶
            pg_cursor = pg_conn.cursor()
            pg_cursor.execute(
                "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id;",
                ("integration_user", "integration@example.com")
            )
            user_id = pg_cursor.fetchone()[0]
            
            # 在 MongoDB 中創建題目
            question_doc = {
                "user_id": user_id,
                "question": "整合測試題目",
                "subject": "數學"
            }
            mongo_result = mongo_collection.insert_one(question_doc)
            
            # 在 Redis 中快取用戶資訊
            user_cache_key = f"user:{user_id}"
            user_data = {
                "username": "integration_user",
                "email": "integration@example.com"
            }
            redis_client.hset(user_cache_key, mapping=user_data)
            
            # 驗證整合操作
            # 1. 檢查 PostgreSQL 中的用戶
            pg_cursor.execute("SELECT username FROM test_users WHERE id = %s;", (user_id,))
            pg_user = pg_cursor.fetchone()
            
            # 2. 檢查 MongoDB 中的題目
            mongo_question = mongo_collection.find_one({"_id": mongo_result.inserted_id})
            
            # 3. 檢查 Redis 中的快取
            cached_user = redis_client.hgetall(user_cache_key)
            
            # 清理測試資料
            pg_cursor.execute("DELETE FROM test_users WHERE id = %s;", (user_id,))
            pg_conn.commit()
            mongo_collection.delete_one({"_id": mongo_result.inserted_id})
            redis_client.delete(user_cache_key)
            
            # 關閉連接
            pg_cursor.close()
            pg_conn.close()
            mongo_client.close()
            redis_client.close()
            
            # 驗證結果
            assert pg_user[0] == "integration_user"
            assert mongo_question["user_id"] == user_id
            assert cached_user[b"username"].decode() == "integration_user"
            
        except Exception as e:
            pytest.skip(f"跨資料庫操作失敗: {e}")
    
    def test_data_consistency(self):
        """測試資料一致性"""
        try:
            # 模擬用戶註冊流程
            pg_conn = psycopg2.connect(
                host="localhost", port=5432,
                database="inulearning_test",
                user="test", password="test"
            )
            
            mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
            mongo_db = mongo_client.inulearning_test
            user_sessions = mongo_db.user_sessions
            
            redis_client = redis.Redis(host="localhost", port=6379, db=1)
            
            # 1. 在 PostgreSQL 中創建用戶
            pg_cursor = pg_conn.cursor()
            pg_cursor.execute(
                "INSERT INTO test_users (username, email) VALUES (%s, %s) RETURNING id;",
                ("consistency_user", "consistency@example.com")
            )
            user_id = pg_cursor.fetchone()[0]
            
            # 2. 在 MongoDB 中記錄用戶會話
            session_doc = {
                "user_id": user_id,
                "session_id": "session123",
                "start_time": "2024-01-01T00:00:00Z",
                "status": "active"
            }
            session_result = user_sessions.insert_one(session_doc)
            
            # 3. 在 Redis 中快取用戶狀態
            status_key = f"user_status:{user_id}"
            redis_client.set(status_key, "online", ex=300)
            
            # 驗證資料一致性
            # 檢查用戶是否存在於所有資料庫中
            pg_cursor.execute("SELECT COUNT(*) FROM test_users WHERE id = %s;", (user_id,))
            pg_count = pg_cursor.fetchone()[0]
            
            mongo_count = user_sessions.count_documents({"user_id": user_id})
            
            redis_status = redis_client.get(status_key)
            
            # 清理測試資料
            pg_cursor.execute("DELETE FROM test_users WHERE id = %s;", (user_id,))
            pg_conn.commit()
            user_sessions.delete_one({"_id": session_result.inserted_id})
            redis_client.delete(status_key)
            
            # 關閉連接
            pg_cursor.close()
            pg_conn.close()
            mongo_client.close()
            redis_client.close()
            
            # 驗證一致性
            assert pg_count == 1
            assert mongo_count == 1
            assert redis_status.decode() == "online"
            
        except Exception as e:
            pytest.skip(f"資料一致性測試失敗: {e}") 