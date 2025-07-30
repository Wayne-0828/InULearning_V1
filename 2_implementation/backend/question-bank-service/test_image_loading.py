#!/usr/bin/env python3
"""
測試圖片題目載入
驗證包含image_path的題目能正確載入並對應圖片
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from load_rawdata import DataLoader
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_image_question_loading():
    """測試圖片題目載入"""
    logger.info("🖼️ 測試圖片題目載入功能...")
    
    loader = DataLoader()
    
    try:
        await loader.initialize()
        
        # 清空測試資料
        await loader.db.questions.delete_many({"source_file": "test_image_sample.json"})
        logger.info("✅ 清空測試資料")
        
        # 載入測試檔案
        test_file = Path(__file__).parent / "test_image_sample.json"
        
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"📖 載入測試檔案: {len(data)} 道題目")
        
        # 處理每道題目
        for item in data:
            await loader.process_question_item(item, test_file)
        
        logger.info(f"✅ 成功載入 {loader.question_count} 道題目")
        
        # 驗證載入結果
        loaded_questions = await loader.db.questions.find({
            "source_file": "test_image_sample.json"
        }).to_list(None)
        
        logger.info(f"🔍 驗證結果: 找到 {len(loaded_questions)} 道題目")
        
        for i, question in enumerate(loaded_questions, 1):
            logger.info(f"\n📝 題目 {i}:")
            logger.info(f"  內容: {question['content']}")
            logger.info(f"  科目: {question['subject']}")
            logger.info(f"  年級: {question['grade']}")
            logger.info(f"  出版社: {question['publisher']}")
            logger.info(f"  章節: {question['chapter']}")
            logger.info(f"  圖片檔名: {question['image_filename']}")
            logger.info(f"  圖片URL: {question['image_url']}")
            
            # 檢查圖片是否存在於MinIO
            if question['image_filename']:
                object_name = f"images/{question['image_filename']}"
                try:
                    stat = loader.minio_client.stat_object(
                        "question-bank", 
                        object_name
                    )
                    logger.info(f"  ✅ 圖片存在於MinIO ({stat.size} bytes)")
                except Exception as e:
                    logger.warning(f"  ⚠️ 圖片不存在於MinIO: {e}")
            
            # 檢查選項格式
            logger.info(f"  選項數量: {len(question['options'])}")
            for option in question['options']:
                logger.info(f"    {option['key']}: {option['text']}")
            
            logger.info(f"  正確答案: {question['correct_answer']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False
    
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def verify_image_exists():
    """驗證圖片檔案是否存在"""
    logger.info("🔍 驗證圖片檔案...")
    
    image_filename = "d7a77ba957076eed2594b54bd0a92a5b0d9c96aca84a5d5a35514fae938c9ec8.jpg"
    
    # 檢查本地檔案
    seeds_path = Path(__file__).parent.parent.parent / "database" / "seeds" / "全題庫"
    
    found_paths = []
    for images_dir in seeds_path.rglob("images"):
        image_path = images_dir / image_filename
        if image_path.exists():
            found_paths.append(image_path)
            logger.info(f"✅ 找到圖片: {image_path}")
    
    if not found_paths:
        logger.warning(f"⚠️ 本地找不到圖片: {image_filename}")
        return False
    
    # 檢查MinIO
    loader = DataLoader()
    try:
        await loader.initialize()
        
        object_name = f"images/{image_filename}"
        try:
            stat = loader.minio_client.stat_object(
                "question-bank",
                object_name
            )
            logger.info(f"✅ MinIO中找到圖片: {object_name} ({stat.size} bytes)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ MinIO中找不到圖片: {object_name}")
            logger.info("💡 可能需要重新執行圖片上傳")
            return False
    
    except Exception as e:
        logger.error(f"❌ MinIO連接失敗: {e}")
        return False
    
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def main():
    """主要測試函數"""
    logger.info("🚀 開始測試圖片題目載入...")
    
    # 先驗證圖片是否存在
    image_exists = await verify_image_exists()
    
    if not image_exists:
        logger.warning("⚠️ 圖片不存在，但仍會測試題目載入功能")
    
    logger.info("\n" + "="*50 + "\n")
    
    # 測試題目載入
    success = await test_image_question_loading()
    
    if success:
        logger.info("🎉 圖片題目載入測試成功！")
    else:
        logger.error("❌ 圖片題目載入測試失敗！")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)