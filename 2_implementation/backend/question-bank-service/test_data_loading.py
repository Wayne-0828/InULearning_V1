#!/usr/bin/env python3
"""
測試資料載入腳本
用於驗證MongoDB和MinIO連接以及資料載入功能
"""

import asyncio
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


async def test_connections():
    """測試連接"""
    loader = DataLoader()
    
    try:
        await loader.initialize()
        logger.info("✅ 所有連接測試成功")
        return True
    except Exception as e:
        logger.error(f"❌ 連接測試失敗: {e}")
        return False
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def test_sample_data_loading():
    """測試載入少量範例資料"""
    loader = DataLoader()
    
    try:
        await loader.initialize()
        
        # 創建測試資料
        test_questions = [
            {
                "grade": "7A",
                "subject": "數學",
                "publisher": "南一",
                "chapter": "第一章",
                "topic": "整數運算",
                "knowledge_point": ["加法", "減法"],
                "difficulty": "easy",
                "question": "計算 3 + 5 = ?",
                "options": {
                    "A": "6",
                    "B": "7", 
                    "C": "8",
                    "D": "9"
                },
                "answer": "C",
                "explanation": "3 + 5 = 8"
            },
            {
                "grade": "7A",
                "subject": "國文",
                "publisher": "康軒",
                "chapter": "第二章",
                "topic": "現代詩",
                "knowledge_point": ["修辭", "意象"],
                "difficulty": "medium",
                "question": "下列何者是擬人法的運用？",
                "options": {
                    "A": "白雲像棉花",
                    "B": "花兒在微笑",
                    "C": "聲音很大",
                    "D": "天空很藍"
                },
                "answer": "B",
                "explanation": "擬人法是將非人的事物賦予人的特性，花兒微笑即是擬人法。"
            }
        ]
        
        # 處理測試資料
        for item in test_questions:
            await loader.process_question_item(item, Path("test_file.json"))
        
        logger.info(f"✅ 測試資料載入成功，載入 {loader.question_count} 道題目")
        
        # 驗證資料
        count = await loader.db.questions.count_documents({})
        logger.info(f"📊 資料庫中共有 {count} 道題目")
        
        # 查詢範例
        sample_question = await loader.db.questions.find_one({"subject": "數學"})
        if sample_question:
            logger.info(f"📝 範例題目: {sample_question['content']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試資料載入失敗: {e}")
        return False
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


async def main():
    """主要測試函數"""
    logger.info("🚀 開始測試資料載入功能...")
    
    # 測試連接
    logger.info("1️⃣ 測試資料庫連接...")
    if not await test_connections():
        logger.error("❌ 連接測試失敗，請檢查 MongoDB 和 MinIO 服務")
        return
    
    # 測試資料載入
    logger.info("2️⃣ 測試範例資料載入...")
    if not await test_sample_data_loading():
        logger.error("❌ 資料載入測試失敗")
        return
    
    logger.info("🎉 所有測試完成！")


if __name__ == "__main__":
    asyncio.run(main())