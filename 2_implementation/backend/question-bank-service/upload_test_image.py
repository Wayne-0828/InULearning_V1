#!/usr/bin/env python3
"""
上傳測試圖片到MinIO
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


async def upload_test_image():
    """上傳測試圖片"""
    logger.info("🖼️ 上傳測試圖片到MinIO...")
    
    loader = DataLoader()
    
    try:
        await loader.initialize()
        
        # 找到圖片檔案
        image_filename = "d7a77ba957076eed2594b54bd0a92a5b0d9c96aca84a5d5a35514fae938c9ec8.jpg"
        seeds_path = Path(__file__).parent.parent.parent / "database" / "seeds" / "全題庫"
        
        image_path = None
        for images_dir in seeds_path.rglob("images"):
            test_path = images_dir / image_filename
            if test_path.exists():
                image_path = test_path
                break
        
        if not image_path:
            logger.error(f"❌ 找不到圖片檔案: {image_filename}")
            return False
        
        logger.info(f"📁 找到圖片: {image_path}")
        
        # 上傳圖片
        await loader.upload_image(image_path)
        logger.info("✅ 圖片上傳成功")
        
        # 驗證上傳
        object_name = f"images/{image_filename}"
        try:
            stat = loader.minio_client.stat_object("question-bank", object_name)
            logger.info(f"✅ 驗證成功: {object_name} ({stat.size} bytes)")
            return True
        except Exception as e:
            logger.error(f"❌ 驗證失敗: {e}")
            return False
    
    except Exception as e:
        logger.error(f"❌ 上傳失敗: {e}")
        return False
    
    finally:
        if loader.mongodb_client:
            loader.mongodb_client.close()


if __name__ == "__main__":
    success = asyncio.run(upload_test_image())
    sys.exit(0 if success else 1)