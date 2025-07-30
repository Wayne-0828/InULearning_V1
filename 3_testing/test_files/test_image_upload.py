#!/usr/bin/env python3
"""
測試圖片上傳功能
先上傳少量圖片進行測試
"""

import os
import sys
import asyncio
import aiofiles
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestImageUploader:
    """測試圖片上傳器"""
    
    def __init__(self):
        self.minio_client = None
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.seeds_path = Path(__file__).parent / "2_implementation" / "database" / "seeds" / "全題庫"
        
    def initialize(self):
        """初始化MinIO連接"""
        try:
            self.minio_client = Minio(
                'localhost:9000',
                access_key='aipe-tester',
                secret_key='aipe-tester',
                secure=False
            )
            
            bucket_name = 'question-images'
            
            # 確保bucket存在
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
                logger.info(f"✅ 創建 MinIO bucket: {bucket_name}")
            else:
                logger.info(f"✅ MinIO bucket 已存在: {bucket_name}")
                
            self.bucket_name = bucket_name
            
        except Exception as e:
            logger.error(f"❌ MinIO 初始化失敗: {e}")
            raise

    async def test_upload_sample_images(self):
        """測試上傳少量圖片"""
        logger.info(f"開始測試圖片上傳...")
        logger.info(f"掃描目錄: {self.seeds_path}")
        
        if not self.seeds_path.exists():
            logger.error(f"❌ seeds目錄不存在: {self.seeds_path}")
            return
        
        # 查找第一個有圖片的目錄
        test_images = []
        for root, dirs, files in os.walk(self.seeds_path):
            if 'images' in dirs:
                image_dir = Path(root) / 'images'
                logger.info(f"檢查目錄: {image_dir}")
                
                # 找前5張圖片進行測試
                for pattern in ["*.jpg", "*.jpeg", "*.png"]:
                    found_images = list(image_dir.glob(pattern))
                    test_images.extend(found_images[:5])
                    if len(test_images) >= 5:
                        break
                
                if len(test_images) >= 5:
                    break
        
        if not test_images:
            logger.error("❌ 沒有找到任何圖片檔案")
            return
        
        logger.info(f"找到 {len(test_images)} 張測試圖片")
        
        # 上傳測試圖片
        for i, image_path in enumerate(test_images):
            logger.info(f"上傳第 {i+1}/{len(test_images)} 張: {image_path.name}")
            try:
                await self.upload_image(image_path)
            except Exception as e:
                logger.error(f"上傳失敗: {e}")
        
        logger.info(f"🎉 測試完成！")
        logger.info(f"   - 上傳成功: {self.uploaded_count} 張")
        logger.info(f"   - 跳過重複: {self.skipped_count} 張")
        logger.info(f"   - 上傳失敗: {self.error_count} 張")

    async def upload_image(self, image_path: Path):
        """上傳單張圖片"""
        filename = image_path.name
        
        # 檢查圖片是否已存在
        try:
            self.minio_client.stat_object(self.bucket_name, filename)
            logger.info(f"圖片已存在，跳過: {filename}")
            self.skipped_count += 1
            return
        except S3Error as e:
            if e.code != 'NoSuchKey':
                raise
        
        # 上傳圖片
        try:
            # 根據檔案副檔名設定content_type
            content_type = 'image/jpeg'
            if filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            
            # 使用同步方式讀取檔案並上傳
            with open(image_path, 'rb') as f:
                file_data = f.read()
                
            from io import BytesIO
            data_stream = BytesIO(file_data)
            
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=data_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            logger.info(f"✅ 上傳成功: {filename} ({len(file_data)} bytes)")
            self.uploaded_count += 1
            
        except Exception as e:
            logger.error(f"❌ 上傳失敗 {filename}: {e}")
            self.error_count += 1
            raise

    def check_minio_status(self):
        """檢查MinIO狀態"""
        try:
            # 列出所有buckets
            buckets = self.minio_client.list_buckets()
            logger.info("📊 MinIO狀態:")
            for bucket in buckets:
                logger.info(f"  - Bucket: {bucket.name}")
                
                # 統計該bucket中的物件數量
                objects = list(self.minio_client.list_objects(bucket.name))
                logger.info(f"    物件數量: {len(objects)}")
                
                if len(objects) > 0:
                    logger.info(f"    前3個物件:")
                    for i, obj in enumerate(objects[:3]):
                        logger.info(f"      {i+1}. {obj.object_name}")
                        
        except Exception as e:
            logger.error(f"❌ 檢查MinIO狀態失敗: {e}")

async def main():
    """主程式"""
    uploader = TestImageUploader()
    
    try:
        # 初始化連接
        uploader.initialize()
        
        # 檢查MinIO狀態
        uploader.check_minio_status()
        
        # 測試上傳圖片
        await uploader.test_upload_sample_images()
        
        # 再次檢查狀態
        logger.info("\n" + "="*50)
        logger.info("上傳後的MinIO狀態:")
        uploader.check_minio_status()
        
    except Exception as e:
        logger.error(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())