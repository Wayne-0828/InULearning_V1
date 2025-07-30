#!/usr/bin/env python3
"""
測試包含圖片的題目處理
驗證圖片檔名提取和對應功能
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from load_rawdata import DataLoader
from minio import Minio
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_image_question_processing():
    """測試包含圖片的題目處理"""
    logger.info("🖼️ 測試圖片題目處理功能...")
    
    loader = DataLoader()
    
    # 測試您提供的範例題目
    sample_question = {
        "question": "附圖中的方向標空格應填入哪一個方位？",
        "options": {
            "A": "東北",
            "B": "西北", 
            "C": "東南",
            "D": "西南。"
        },
        "image_path": "images/d7a77ba957076eed2594b54bd0a92a5b0d9c96aca84a5d5a35514fae938c9ec8.jpg",
        "scope": "國中",
        "grade": "7A",
        "subject": "地理",
        "semester": "113上",
        "publisher": "康軒",
        "chapter": "1-1 位置、地圖與座標系統我的位置在哪裡",
        "answer": "D"
    }
    
    # 測試圖片檔名提取
    question_text = sample_question.get('question', '')
    image_filename = loader.extract_image_filename(question_text, sample_question)
    
    logger.info(f"📝 題目內容: {question_text}")
    logger.info(f"🖼️ 提取的圖片檔名: {image_filename}")
    
    if image_filename:
        logger.info("✅ 成功提取圖片檔名")
        
        # 檢查圖片是否存在於MinIO中
        try:
            await loader.initialize()
            
            # 檢查圖片是否存在
            object_name = f"images/{image_filename}"
            
            try:
                # 嘗試獲取圖片資訊
                stat = loader.minio_client.stat_object(loader.minio_client._bucket_name, object_name)
                logger.info(f"✅ 圖片存在於MinIO: {object_name}")
                logger.info(f"📊 圖片大小: {stat.size} bytes")
                logger.info(f"📅 上傳時間: {stat.last_modified}")
                
                # 生成圖片URL
                image_url = f"/api/v1/images/{image_filename}"
                logger.info(f"🔗 圖片URL: {image_url}")
                
            except Exception as e:
                logger.warning(f"⚠️ 圖片不存在於MinIO: {object_name}")
                logger.info("💡 這可能是因為此特定圖片檔案不在當前的seeds資料中")
        
        except Exception as e:
            logger.error(f"❌ MinIO連接失敗: {e}")
    
    else:
        logger.warning("⚠️ 無法提取圖片檔名")
    
    # 測試標準化格式
    try:
        standardized = await loader.standardize_question_format(sample_question, Path("test.json"))
        logger.info("📋 標準化後的題目格式:")
        logger.info(f"  題目ID: {standardized['question_id']}")
        logger.info(f"  科目: {standardized['subject']}")
        logger.info(f"  年級: {standardized['grade']}")
        logger.info(f"  圖片檔名: {standardized['image_filename']}")
        logger.info(f"  圖片URL: {standardized['image_url']}")
        
    except Exception as e:
        logger.error(f"❌ 標準化處理失敗: {e}")
    
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def check_existing_image_questions():
    """檢查資料庫中已載入的圖片題目"""
    logger.info("🔍 檢查資料庫中的圖片題目...")
    
    loader = DataLoader()
    
    try:
        await loader.initialize()
        
        # 查詢包含圖片的題目
        image_questions = await loader.db.questions.find({
            "image_filename": {"$ne": None}
        }).limit(10).to_list(None)
        
        logger.info(f"📊 找到 {len(image_questions)} 道包含圖片的題目")
        
        for i, question in enumerate(image_questions, 1):
            logger.info(f"📝 題目 {i}:")
            logger.info(f"  內容: {question['content'][:100]}...")
            logger.info(f"  科目: {question['subject']}")
            logger.info(f"  圖片檔名: {question['image_filename']}")
            logger.info(f"  圖片URL: {question['image_url']}")
            
            # 驗證圖片是否存在
            if question['image_filename']:
                object_name = f"images/{question['image_filename']}"
                try:
                    stat = loader.minio_client.stat_object(loader.minio_client._bucket_name, object_name)
                    logger.info(f"  ✅ 圖片存在 ({stat.size} bytes)")
                except:
                    logger.info(f"  ❌ 圖片不存在")
            
            logger.info("")
    
    except Exception as e:
        logger.error(f"❌ 查詢失敗: {e}")
    
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def main():
    """主要測試函數"""
    logger.info("🚀 開始測試圖片題目功能...")
    
    # 測試圖片題目處理
    await test_image_question_processing()
    
    logger.info("\n" + "="*50 + "\n")
    
    # 檢查現有資料
    await check_existing_image_questions()
    
    logger.info("🎉 測試完成！")


if __name__ == "__main__":
    asyncio.run(main())