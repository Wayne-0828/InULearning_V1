"""
Redis 資料庫連接模組
提供 Redis 快取和會話管理
"""

import os
import logging
import json
from typing import Optional, Any, Dict, List
from redis import Redis, ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis 資料庫管理器"""
    
    def __init__(self):
        """初始化資料庫管理器"""
        self.redis_client = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化資料庫連接"""
        try:
            # 從環境變數取得資料庫配置
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))
            redis_password = os.getenv("REDIS_PASSWORD")
            redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
            
            # 建立連接池
            connection_pool = ConnectionPool(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                ssl=redis_ssl,
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True
            )
            
            # 建立 Redis 客戶端
            self.redis_client = Redis(connection_pool=connection_pool)
            
            # 測試連接
            self.redis_client.ping()
            
            logger.info("Redis 連接初始化成功")
            
        except Exception as e:
            logger.error(f"Redis 連接初始化失敗: {e}")
            raise
    
    def get_client(self) -> Redis:
        """取得 Redis 客戶端"""
        if not self.redis_client:
            raise RuntimeError("Redis 客戶端未初始化")
        return self.redis_client
    
    def test_connection(self) -> bool:
        """測試資料庫連接"""
        try:
            self.redis_client.ping()
            return True
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis 連接測試失敗: {e}")
            return False
    
    def set_key(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """設定鍵值對"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            self.redis_client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"設定鍵值對失敗: {key} - {e}")
            return False
    
    def get_key(self, key: str) -> Optional[Any]:
        """取得鍵值"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # 嘗試解析 JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"取得鍵值失敗: {key} - {e}")
            return None
    
    def delete_key(self, key: str) -> bool:
        """刪除鍵"""
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"刪除鍵失敗: {key} - {e}")
            return False
    
    def exists_key(self, key: str) -> bool:
        """檢查鍵是否存在"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"檢查鍵存在失敗: {key} - {e}")
            return False
    
    def set_hash(self, name: str, mapping: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """設定雜湊表"""
        try:
            # 將複雜物件轉換為 JSON 字串
            json_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    json_mapping[k] = json.dumps(v, ensure_ascii=False)
                else:
                    json_mapping[k] = str(v)
            
            self.redis_client.hset(name, mapping=json_mapping)
            
            if expire:
                self.redis_client.expire(name, expire)
            
            return True
        except Exception as e:
            logger.error(f"設定雜湊表失敗: {name} - {e}")
            return False
    
    def get_hash(self, name: str, key: Optional[str] = None) -> Optional[Any]:
        """取得雜湊表值"""
        try:
            if key:
                value = self.redis_client.hget(name, key)
                if value is None:
                    return None
                
                # 嘗試解析 JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                # 取得整個雜湊表
                hash_data = self.redis_client.hgetall(name)
                result = {}
                for k, v in hash_data.items():
                    try:
                        result[k] = json.loads(v)
                    except json.JSONDecodeError:
                        result[k] = v
                return result
                
        except Exception as e:
            logger.error(f"取得雜湊表失敗: {name} - {e}")
            return None
    
    def set_list(self, name: str, values: List[Any], expire: Optional[int] = None) -> bool:
        """設定列表"""
        try:
            # 清空現有列表
            self.redis_client.delete(name)
            
            # 添加新值
            for value in values:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                self.redis_client.rpush(name, value)
            
            if expire:
                self.redis_client.expire(name, expire)
            
            return True
        except Exception as e:
            logger.error(f"設定列表失敗: {name} - {e}")
            return False
    
    def get_list(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """取得列表"""
        try:
            values = self.redis_client.lrange(name, start, end)
            result = []
            
            for value in values:
                try:
                    result.append(json.loads(value))
                except json.JSONDecodeError:
                    result.append(value)
            
            return result
        except Exception as e:
            logger.error(f"取得列表失敗: {name} - {e}")
            return []
    
    def increment_counter(self, key: str, amount: int = 1, expire: Optional[int] = None) -> Optional[int]:
        """增加計數器"""
        try:
            result = self.redis_client.incrby(key, amount)
            
            if expire:
                self.redis_client.expire(key, expire)
            
            return result
        except Exception as e:
            logger.error(f"增加計數器失敗: {key} - {e}")
            return None
    
    def get_counter(self, key: str) -> int:
        """取得計數器值"""
        try:
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"取得計數器失敗: {key} - {e}")
            return 0
    
    def set_session(self, session_id: str, session_data: Dict[str, Any], expire: int = 3600) -> bool:
        """設定會話資料"""
        return self.set_key(f"session:{session_id}", session_data, expire)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """取得會話資料"""
        return self.get_key(f"session:{session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """刪除會話資料"""
        return self.delete_key(f"session:{session_id}")
    
    def set_cache(self, key: str, data: Any, expire: int = 300) -> bool:
        """設定快取資料"""
        return self.set_key(f"cache:{key}", data, expire)
    
    def get_cache(self, key: str) -> Optional[Any]:
        """取得快取資料"""
        return self.get_key(f"cache:{key}")
    
    def delete_cache(self, key: str) -> bool:
        """刪除快取資料"""
        return self.delete_key(f"cache:{key}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """取得資料庫資訊"""
        try:
            info = self.redis_client.info()
            
            return {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "uptime_in_seconds": info.get("uptime_in_seconds"),
                "db_size": len(self.redis_client.keys("*"))
            }
            
        except Exception as e:
            logger.error(f"取得資料庫資訊失敗: {e}")
            return {}
    
    def clear_database(self) -> bool:
        """清空資料庫"""
        try:
            self.redis_client.flushdb()
            logger.info("Redis 資料庫清空成功")
            return True
        except Exception as e:
            logger.error(f"Redis 資料庫清空失敗: {e}")
            return False
    
    def close_connection(self):
        """關閉資料庫連接"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis 連接已關閉")

# 全域資料庫管理器實例
redis_manager = RedisManager()

def get_redis() -> Redis:
    """取得 Redis 客戶端的便捷函數"""
    return redis_manager.get_client() 