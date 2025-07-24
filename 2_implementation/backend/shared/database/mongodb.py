"""
MongoDB 資料庫連接模組
提供 MongoDB 資料庫連接和集合管理
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi
import time

logger = logging.getLogger(__name__)

class MongoDBManager:
    """MongoDB 資料庫管理器"""
    
    def __init__(self):
        """初始化資料庫管理器"""
        self.client = None
        self.db = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化資料庫連接"""
        try:
            # 從環境變數取得資料庫配置
            mongo_host = os.getenv("MONGO_HOST", "localhost")
            mongo_port = int(os.getenv("MONGO_PORT", "27017"))
            mongo_db = os.getenv("MONGO_DB", "inulearning")
            mongo_user = os.getenv("MONGO_USER")
            mongo_password = os.getenv("MONGO_PASSWORD")
            
            # 建立連接字串
            if mongo_user and mongo_password:
                # 有認證的連接
                connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin"
            else:
                # 無認證的連接
                connection_string = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
            
            # 建立客戶端
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                tlsCAFile=certifi.where() if os.getenv("MONGO_TLS", "false").lower() == "true" else None
            )
            
            # 取得資料庫實例
            self.db = self.client[mongo_db]
            
            # 測試連接
            self.client.admin.command('ping')
            
            logger.info("MongoDB 連接初始化成功")
            
        except Exception as e:
            logger.error(f"MongoDB 連接初始化失敗: {e}")
            raise
    
    def get_database(self) -> Database:
        """取得資料庫實例"""
        if not self.db:
            raise RuntimeError("MongoDB 資料庫未初始化")
        return self.db
    
    def get_collection(self, collection_name: str) -> Collection:
        """取得集合實例"""
        if not self.db:
            raise RuntimeError("MongoDB 資料庫未初始化")
        return self.db[collection_name]
    
    def test_connection(self) -> bool:
        """測試資料庫連接"""
        try:
            self.client.admin.command('ping')
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB 連接測試失敗: {e}")
            return False
    
    def create_indexes(self, collection_name: str, indexes: List[Dict[str, Any]]) -> bool:
        """為指定集合建立索引"""
        try:
            collection = self.get_collection(collection_name)
            for index_spec in indexes:
                collection.create_index(**index_spec)
            logger.info(f"集合 {collection_name} 索引建立成功")
            return True
        except Exception as e:
            logger.error(f"集合 {collection_name} 索引建立失敗: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """取得資料庫資訊"""
        try:
            # 取得資料庫統計資訊
            db_stats = self.db.command("dbStats")
            
            # 取得集合列表
            collections = self.db.list_collection_names()
            
            # 取得每個集合的統計資訊
            collection_stats = {}
            for collection_name in collections:
                try:
                    coll_stats = self.db.command("collStats", collection_name)
                    collection_stats[collection_name] = {
                        "count": coll_stats.get("count", 0),
                        "size": coll_stats.get("size", 0),
                        "avgObjSize": coll_stats.get("avgObjSize", 0),
                        "storageSize": coll_stats.get("storageSize", 0),
                        "indexes": coll_stats.get("nindexes", 0)
                    }
                except Exception as e:
                    logger.warning(f"取得集合 {collection_name} 統計資訊失敗: {e}")
                    collection_stats[collection_name] = {"error": str(e)}
            
            return {
                "database_name": self.db.name,
                "collections": collections,
                "collection_count": len(collections),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "index_size": db_stats.get("indexSize", 0),
                "collection_stats": collection_stats
            }
            
        except Exception as e:
            logger.error(f"取得資料庫資訊失敗: {e}")
            return {}
    
    def backup_collection(self, collection_name: str, backup_name: str = None) -> bool:
        """備份集合"""
        try:
            if not backup_name:
                backup_name = f"{collection_name}_backup_{int(time.time())}"
            
            # 複製集合
            self.db.command("cloneCollection", f"{self.db.name}.{collection_name}", 
                           to=f"{self.db.name}.{backup_name}")
            
            logger.info(f"集合 {collection_name} 備份成功: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"集合 {collection_name} 備份失敗: {e}")
            return False
    
    def restore_collection(self, backup_name: str, target_name: str) -> bool:
        """還原集合"""
        try:
            # 檢查備份集合是否存在
            if backup_name not in self.db.list_collection_names():
                logger.error(f"備份集合 {backup_name} 不存在")
                return False
            
            # 刪除目標集合（如果存在）
            if target_name in self.db.list_collection_names():
                self.db[target_name].drop()
            
            # 複製備份集合到目標集合
            self.db.command("cloneCollection", f"{self.db.name}.{backup_name}", 
                           to=f"{self.db.name}.{target_name}")
            
            logger.info(f"集合還原成功: {backup_name} -> {target_name}")
            return True
            
        except Exception as e:
            logger.error(f"集合還原失敗: {e}")
            return False
    
    def close_connection(self):
        """關閉資料庫連接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 連接已關閉")

# 全域資料庫管理器實例
mongodb_manager = MongoDBManager()

def get_mongodb() -> Database:
    """取得 MongoDB 資料庫實例的便捷函數"""
    return mongodb_manager.get_database()

def get_collection(collection_name: str) -> Collection:
    """取得 MongoDB 集合實例的便捷函數"""
    return mongodb_manager.get_collection(collection_name) 