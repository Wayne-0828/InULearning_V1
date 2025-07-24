#!/usr/bin/env python3
"""
資料庫一致性檢查腳本

驗證跨服務的資料一致性，確保資料在不同資料庫間的一致性
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any, List, Optional
import aiohttp
import json
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加 shared 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

try:
    from database.postgresql import get_postgresql_engine, get_postgresql_session
    from database.mongodb import get_mongodb_client, get_mongodb_database
    from database.redis import get_redis_client
    logger.info("✅ 成功導入 shared 資料庫配置")
except ImportError as e:
    logger.warning(f"⚠️ 無法導入 shared 資料庫配置: {e}")

class DataConsistencyChecker:
    """資料一致性檢查器"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.postgresql_engine = None
        self.mongodb_client = None
        self.redis_client = None
    
    async def initialize_connections(self):
        """初始化資料庫連接"""
        try:
            # 初始化 PostgreSQL
            self.postgresql_engine = get_postgresql_engine()
            logger.info("✅ PostgreSQL 連接初始化成功")
            
            # 初始化 MongoDB
            self.mongodb_client = get_mongodb_client()
            self.mongodb_database = get_mongodb_database()
            logger.info("✅ MongoDB 連接初始化成功")
            
            # 初始化 Redis
            self.redis_client = get_redis_client()
            logger.info("✅ Redis 連接初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 資料庫連接初始化失敗: {e}")
            raise
    
    async def check_user_data_consistency(self) -> Dict[str, Any]:
        """檢查用戶資料一致性"""
        try:
            logger.info("🔍 檢查用戶資料一致性...")
            
            # 檢查 PostgreSQL 中的用戶資料
            async with self.postgresql_engine.begin() as conn:
                result = await conn.execute("SELECT COUNT(*) FROM users")
                postgresql_user_count = result.scalar()
            
            # 檢查 Redis 中的用戶快取
            user_cache_keys = await self.redis_client.keys("user:*")
            redis_user_cache_count = len(user_cache_keys)
            
            # 檢查 MongoDB 中是否有相關的用戶活動記錄
            learning_records = self.mongodb_database.learning_records
            mongo_user_activity_count = await learning_records.count_documents({})
            
            consistency_status = "consistent"
            issues = []
            
            # 檢查邏輯：PostgreSQL 應該有用戶資料，Redis 可能有快取，MongoDB 可能有活動記錄
            if postgresql_user_count == 0:
                issues.append("PostgreSQL 中沒有用戶資料")
                consistency_status = "inconsistent"
            
            logger.info(f"   PostgreSQL 用戶數: {postgresql_user_count}")
            logger.info(f"   Redis 用戶快取數: {redis_user_cache_count}")
            logger.info(f"   MongoDB 活動記錄數: {mongo_user_activity_count}")
            
            return {
                "status": consistency_status,
                "postgresql_user_count": postgresql_user_count,
                "redis_user_cache_count": redis_user_cache_count,
                "mongo_user_activity_count": mongo_user_activity_count,
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"❌ 用戶資料一致性檢查失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_question_data_consistency(self) -> Dict[str, Any]:
        """檢查題目資料一致性"""
        try:
            logger.info("🔍 檢查題目資料一致性...")
            
            # 檢查 MongoDB 中的題目資料
            questions_collection = self.mongodb_database.questions
            mongo_question_count = await questions_collection.count_documents({})
            
            # 檢查 Redis 中的題目快取
            question_cache_keys = await self.redis_client.keys("question:*")
            redis_question_cache_count = len(question_cache_keys)
            
            # 檢查 PostgreSQL 中是否有相關的學習記錄
            async with self.postgresql_engine.begin() as conn:
                result = await conn.execute("SELECT COUNT(*) FROM learning_records")
                postgresql_learning_record_count = result.scalar()
            
            consistency_status = "consistent"
            issues = []
            
            # 檢查邏輯：MongoDB 應該有題目資料，Redis 可能有快取，PostgreSQL 可能有學習記錄
            if mongo_question_count == 0:
                issues.append("MongoDB 中沒有題目資料")
                consistency_status = "inconsistent"
            
            logger.info(f"   MongoDB 題目數: {mongo_question_count}")
            logger.info(f"   Redis 題目快取數: {redis_question_cache_count}")
            logger.info(f"   PostgreSQL 學習記錄數: {postgresql_learning_record_count}")
            
            return {
                "status": consistency_status,
                "mongo_question_count": mongo_question_count,
                "redis_question_cache_count": redis_question_cache_count,
                "postgresql_learning_record_count": postgresql_learning_record_count,
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"❌ 題目資料一致性檢查失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_learning_session_consistency(self) -> Dict[str, Any]:
        """檢查學習會話資料一致性"""
        try:
            logger.info("🔍 檢查學習會話資料一致性...")
            
            # 檢查 PostgreSQL 中的學習會話
            async with self.postgresql_engine.begin() as conn:
                result = await conn.execute("SELECT COUNT(*) FROM learning_sessions")
                postgresql_session_count = result.scalar()
                
                result = await conn.execute("SELECT COUNT(*) FROM learning_records")
                postgresql_record_count = result.scalar()
            
            # 檢查 Redis 中的會話狀態
            session_cache_keys = await self.redis_client.keys("session:*")
            redis_session_cache_count = len(session_cache_keys)
            
            consistency_status = "consistent"
            issues = []
            
            # 檢查邏輯：學習記錄數應該大於等於會話數
            if postgresql_record_count < postgresql_session_count:
                issues.append("學習記錄數少於會話數")
                consistency_status = "inconsistent"
            
            logger.info(f"   PostgreSQL 會話數: {postgresql_session_count}")
            logger.info(f"   PostgreSQL 記錄數: {postgresql_record_count}")
            logger.info(f"   Redis 會話快取數: {redis_session_cache_count}")
            
            return {
                "status": consistency_status,
                "postgresql_session_count": postgresql_session_count,
                "postgresql_record_count": postgresql_record_count,
                "redis_session_cache_count": redis_session_cache_count,
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"❌ 學習會話資料一致性檢查失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """執行所有一致性檢查"""
        logger.info("🚀 開始資料庫一致性檢查")
        
        try:
            await self.initialize_connections()
            
            # 執行各種一致性檢查
            self.results["user_data"] = await self.check_user_data_consistency()
            self.results["question_data"] = await self.check_question_data_consistency()
            self.results["learning_session"] = await self.check_learning_session_consistency()
            
        except Exception as e:
            logger.error(f"❌ 一致性檢查執行失敗: {e}")
            self.results["error"] = {"status": "failed", "error": str(e)}
        
        return self.results
    
    def generate_report(self) -> str:
        """生成一致性檢查報告"""
        report = []
        report.append("=" * 80)
        report.append("資料庫一致性檢查報告")
        report.append("=" * 80)
        report.append(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if "error" in self.results:
            report.append("❌ 檢查執行失敗")
            report.append(f"錯誤: {self.results['error']['error']}")
            report.append("=" * 80)
            return "\n".join(report)
        
        # 統計結果
        total_checks = len(self.results)
        consistent_checks = sum(1 for result in self.results.values() if result.get("status") == "consistent")
        inconsistent_checks = sum(1 for result in self.results.values() if result.get("status") == "inconsistent")
        error_checks = sum(1 for result in self.results.values() if result.get("status") == "error")
        
        report.append(f"📊 檢查統計:")
        report.append(f"   - 總檢查項目: {total_checks}")
        report.append(f"   - 一致: {consistent_checks}")
        report.append(f"   - 不一致: {inconsistent_checks}")
        report.append(f"   - 錯誤: {error_checks}")
        report.append("")
        
        # 詳細結果
        for check_name, result in self.results.items():
            status_icon = {
                "consistent": "✅",
                "inconsistent": "⚠️",
                "error": "❌"
            }.get(result.get("status"), "❓")
            
            report.append(f"{status_icon} {check_name.replace('_', ' ').title()}")
            report.append(f"   狀態: {result.get('status', 'unknown')}")
            
            # 顯示具體數據
            for key, value in result.items():
                if key not in ["status", "issues", "error"]:
                    report.append(f"   {key}: {value}")
            
            # 顯示問題
            if "issues" in result and result["issues"]:
                report.append("   問題:")
                for issue in result["issues"]:
                    report.append(f"     - {issue}")
            
            # 顯示錯誤
            if "error" in result:
                report.append(f"   錯誤: {result['error']}")
            
            report.append("")
        
        # 建議
        report.append("💡 建議:")
        if inconsistent_checks == 0 and error_checks == 0:
            report.append("   - 所有資料庫資料一致性良好")
            report.append("   - 可以進行下一步的業務邏輯測試")
        else:
            report.append("   - 檢查不一致的資料項目")
            report.append("   - 確認資料同步機制是否正常")
            report.append("   - 檢查資料庫事務處理")
            if error_checks > 0:
                report.append("   - 檢查資料庫連接和權限")
        
        report.append("=" * 80)
        
        return "\n".join(report)


async def main():
    """主函數"""
    logger.info("🔧 資料庫一致性檢查工具")
    logger.info("=" * 50)
    
    checker = DataConsistencyChecker()
    
    # 執行所有檢查
    results = await checker.run_all_checks()
    
    # 生成報告
    report = checker.generate_report()
    print(report)
    
    # 保存報告到文件
    with open("data_consistency_check_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("📄 一致性檢查報告已保存到 data_consistency_check_report.txt")
    
    # 返回退出碼
    inconsistent_checks = sum(1 for result in results.values() if result.get("status") == "inconsistent")
    error_checks = sum(1 for result in results.values() if result.get("status") == "error")
    return 0 if inconsistent_checks == 0 and error_checks == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("⚠️ 檢查被用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 檢查執行失敗: {e}")
        sys.exit(1) 