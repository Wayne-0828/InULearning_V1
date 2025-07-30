#!/usr/bin/env python3 
"""
檢查題目與圖片的關聯情況
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from minio import Minio
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_image_links():
    """檢查題目與圖片的關聯情況"""
    
    # 連接MongoDB
    client = AsyncIOMotorClient('mongodb://aipe-tester:aipe-tester@localhost:27017/inulearning?authSource=admin')
    db = client.inulearning
    
    # 連接MinIO
    minio_client = Minio(
        'localhost:9000',
        access_key='aipe-tester',
        secret_key='aipe-tester',
        secure=False
    )
    
    try:
        # 統計題目總數
        total_questions = await db.questions.count_documents({})
        logger.info(f"📊 資料庫中題目總數: {total_questions:,}")
        
        # 統計有圖片檔名的題目數量
        questions_with_image_filename = await db.questions.count_documents({
            'image_filename': {'$exists': True, '$ne': None, '$ne': ''}
        })
        logger.info(f"📸 有image_filename的題目: {questions_with_image_filename:,}")
        
        # 統計有圖片URL的題目數量
        questions_with_image_url = await db.questions.count_documents({
            'image_url': {'$exists': True, '$ne': None, '$ne': ''}
        })
        logger.info(f"🔗 有image_url的題目: {questions_with_image_url:,}")
        
        # 檢查MinIO中的圖片數量
        try:
            minio_objects = list(minio_client.list_objects('question-images'))
            minio_image_count = len(minio_objects)
            logger.info(f"🗄️  MinIO中的圖片數量: {minio_image_count:,}")
        except Exception as e:
            logger.error(f"❌ 無法連接MinIO: {e}")
            minio_image_count = 0
            minio_objects = []
        
        # 取樣檢查前10個有圖片的題目
        logger.info(f"\n📋 前10個有圖片的題目:")
        cursor = db.questions.find({
            'image_filename': {'$exists': True, '$ne': None, '$ne': ''}
        }).limit(10)
        
        sample_questions = await cursor.to_list(length=10)
        
        for i, q in enumerate(sample_questions, 1):
            logger.info(f"  {i}. 題目: {q.get('question', 'N/A')[:50]}...")
            logger.info(f"     科目: {q.get('subject', 'N/A')}")
            logger.info(f"     圖片檔名: {q.get('image_filename', 'N/A')}")
            logger.info(f"     圖片URL: {q.get('image_url', 'N/A')}")
            
            # 檢查圖片是否存在於MinIO中
            image_filename = q.get('image_filename')
            if image_filename:
                image_exists = any(obj.object_name == image_filename for obj in minio_objects)
                logger.info(f"     MinIO中存在: {'✅' if image_exists else '❌'}")
            logger.info("")
        
        # 統計各科目的圖片情況
        logger.info(f"📊 各科目圖片情況:")
        pipeline = [
            {'$match': {'image_filename': {'$exists': True, '$ne': None, '$ne': ''}}},
            {'$group': {
                '_id': '$subject',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        subject_stats = await db.questions.aggregate(pipeline).to_list(length=None)
        
        for stat in subject_stats:
            subject = stat['_id']
            count = stat['count']
            logger.info(f"  {subject}: {count:,} 題有圖片")
        
        # 檢查圖片檔名格式
        logger.info(f"\n🔍 圖片檔名格式分析:")
        cursor = db.questions.find({
            'image_filename': {'$exists': True, '$ne': None, '$ne': ''}
        })
        
        filename_patterns = {}
        async for q in cursor:
            filename = q.get('image_filename', '')
            if filename:
                # 分析檔名格式
                if len(filename) == 68 and filename.endswith('.jpg'):  # SHA256 + .jpg
                    pattern = 'SHA256.jpg'
                elif filename.endswith('.jpg'):
                    pattern = 'other.jpg'
                elif filename.endswith('.png'):
                    pattern = 'PNG'
                else:
                    pattern = 'unknown'
                
                filename_patterns[pattern] = filename_patterns.get(pattern, 0) + 1
        
        for pattern, count in filename_patterns.items():
            logger.info(f"  {pattern}: {count:,} 個")
        
        # 總結
        logger.info(f"\n" + "="*50)
        logger.info(f"📊 圖片關聯總結:")
        logger.info(f"="*50)
        logger.info(f"總題目數: {total_questions:,}")
        logger.info(f"有圖片檔名的題目: {questions_with_image_filename:,} ({questions_with_image_filename/total_questions*100:.1f}%)")
        logger.info(f"有圖片URL的題目: {questions_with_image_url:,} ({questions_with_image_url/total_questions*100:.1f}%)")
        logger.info(f"MinIO中的圖片: {minio_image_count:,}")
        
        if questions_with_image_filename > 0 and minio_image_count > 0:
            match_rate = min(questions_with_image_filename, minio_image_count) / max(questions_with_image_filename, minio_image_count) * 100
            logger.info(f"圖片匹配度: {match_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ 檢查過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_image_links())