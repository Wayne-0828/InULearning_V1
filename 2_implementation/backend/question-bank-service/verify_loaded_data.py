#!/usr/bin/env python3
"""
驗證載入的資料
"""

import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from minio import Minio
from minio.error import S3Error
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings


async def verify_mongodb():
    """驗證MongoDB中的資料"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    try:
        # 檢查連接
        await client.admin.command('ping')
        logger.info("✅ MongoDB 連接成功")
        
        # 統計題目數量
        total_count = await db.questions.count_documents({})
        logger.info(f"📊 總題目數量: {total_count}")
        
        # 按科目統計
        pipeline = [
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        subject_stats = await db.questions.aggregate(pipeline).to_list(None)
        
        logger.info("📚 按科目統計:")
        for stat in subject_stats:
            logger.info(f"   {stat['_id']}: {stat['count']} 題")
        
        # 按出版社統計
        pipeline = [
            {"$group": {"_id": "$publisher", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        publisher_stats = await db.questions.aggregate(pipeline).to_list(None)
        
        logger.info("📖 按出版社統計:")
        for stat in publisher_stats:
            logger.info(f"   {stat['_id']}: {stat['count']} 題")
        
        # 檢查有圖片的題目
        image_count = await db.questions.count_documents({"image_filename": {"$ne": None}})
        logger.info(f"🖼️  有圖片的題目: {image_count} 題")
        
        # 顯示範例題目
        sample_questions = await db.questions.find().limit(3).to_list(None)
        logger.info("📝 範例題目:")
        for i, q in enumerate(sample_questions, 1):
            logger.info(f"   {i}. {q['question'][:50]}...")
            if q.get('image_filename'):
                logger.info(f"      圖片: {q['image_filename']}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB 驗證失敗: {e}")
    finally:
        client.close()


def verify_minio():
    """驗證MinIO中的資料"""
    try:
        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False
        )
        
        # 檢查bucket是否存在
        if client.bucket_exists(settings.minio_bucket_name):
            logger.info(f"✅ MinIO bucket 存在: {settings.minio_bucket_name}")
            
            # 統計圖片數量
            objects = client.list_objects(settings.minio_bucket_name)
            image_count = sum(1 for obj in objects if obj.object_name.endswith('.jpg'))
            logger.info(f"🖼️  MinIO 中的圖片數量: {image_count}")
            
            # 顯示前幾個圖片檔名
            objects = client.list_objects(settings.minio_bucket_name, recursive=True)
            logger.info("📸 範例圖片檔名:")
            for i, obj in enumerate(objects):
                if i >= 5:  # 只顯示前5個
                    break
                if obj.object_name.endswith('.jpg'):
                    logger.info(f"   {obj.object_name}")
        else:
            logger.error(f"❌ MinIO bucket 不存在: {settings.minio_bucket_name}")
            
    except Exception as e:
        logger.error(f"❌ MinIO 驗證失敗: {e}")


async def main():
    """主程式"""
    logger.info("🔍 開始驗證載入的資料...")
    
    # 設定環境變數
    os.environ.setdefault('MONGODB_URL', 'mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning?authSource=admin')
    os.environ.setdefault('MINIO_ENDPOINT', 'localhost:9000')
    os.environ.setdefault('MINIO_ACCESS_KEY', 'inulearning_admin')
    os.environ.setdefault('MINIO_SECRET_KEY', 'inulearning_password')
    
    # 驗證MongoDB
    await verify_mongodb()
    
    # 驗證MinIO
    verify_minio()
    
    logger.info("🎉 資料驗證完成！")


if __name__ == "__main__":
    asyncio.run(main())