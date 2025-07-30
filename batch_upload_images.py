#!/usr/bin/env python3   上傳圖片
"""
批量上傳圖片到MinIO
分批處理以避免記憶體問題
"""

import os
import sys
import time
import logging
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from io import BytesIO

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchImageUploader:
    """批量圖片上傳器"""
    
    def __init__(self, batch_size=100):
        self.minio_client = None
        self.batch_size = batch_size
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.total_files = 0
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

    def count_total_images(self):
        """統計總圖片數量"""
        logger.info("📊 統計圖片總數...")
        total = 0
        subject_counts = {}
        
        for root, dirs, files in os.walk(self.seeds_path):
            if 'images' in dirs:
                image_dir = Path(root) / 'images'
                subject = Path(root).name
                
                # 統計該目錄的圖片數量
                count = 0
                for pattern in ["*.jpg", "*.jpeg", "*.png"]:
                    count += len(list(image_dir.glob(pattern)))
                
                if count > 0:
                    subject_counts[subject] = count
                    total += count
                    logger.info(f"  {subject}: {count:,} 張圖片")
        
        self.total_files = total
        logger.info(f"📊 總計: {total:,} 張圖片")
        return subject_counts

    def upload_all_images(self):
        """分批上傳所有圖片"""
        start_time = time.time()
        logger.info(f"🚀 開始批量上傳圖片...")
        
        # 統計總數
        subject_counts = self.count_total_images()
        
        # 逐個科目處理
        for root, dirs, files in os.walk(self.seeds_path):
            if 'images' in dirs:
                image_dir = Path(root) / 'images'
                subject = Path(root).name
                
                if subject in subject_counts and subject_counts[subject] > 0:
                    logger.info(f"\n📁 處理科目: {subject} ({subject_counts[subject]:,} 張圖片)")
                    self.upload_from_directory(image_dir, subject)
        
        # 統計結果
        elapsed_time = time.time() - start_time
        logger.info(f"\n🎉 批量上傳完成！")
        logger.info(f"   ⏱️  總耗時: {elapsed_time:.2f} 秒")
        logger.info(f"   ✅ 上傳成功: {self.uploaded_count:,} 張")
        logger.info(f"   ⏭️  跳過重複: {self.skipped_count:,} 張")
        logger.info(f"   ❌ 上傳失敗: {self.error_count:,} 張")
        logger.info(f"   📊 處理進度: {self.uploaded_count + self.skipped_count + self.error_count:,}/{self.total_files:,}")
        
        if self.uploaded_count > 0:
            avg_time = elapsed_time / self.uploaded_count
            logger.info(f"   ⚡ 平均速度: {avg_time:.3f} 秒/張")

    def upload_from_directory(self, image_dir: Path, subject: str):
        """從指定目錄上傳圖片"""
        if not image_dir.exists():
            logger.warning(f"目錄不存在: {image_dir}")
            return
        
        # 收集所有圖片檔案
        image_files = []
        for pattern in ["*.jpg", "*.jpeg", "*.png"]:
            image_files.extend(list(image_dir.glob(pattern)))
        
        if not image_files:
            logger.info(f"目錄中沒有圖片檔案: {image_dir}")
            return
        
        logger.info(f"找到 {len(image_files):,} 個圖片檔案")
        
        # 分批處理
        batch_count = 0
        for i in range(0, len(image_files), self.batch_size):
            batch = image_files[i:i + self.batch_size]
            batch_count += 1
            
            logger.info(f"  📦 處理批次 {batch_count} ({len(batch)} 張圖片)")
            
            for j, image_file in enumerate(batch):
                try:
                    self.upload_image(image_file)
                    
                    # 顯示進度
                    if (self.uploaded_count + self.skipped_count) % 50 == 0:
                        progress = (self.uploaded_count + self.skipped_count + self.error_count) / self.total_files * 100
                        logger.info(f"    📈 整體進度: {progress:.1f}% ({self.uploaded_count + self.skipped_count + self.error_count:,}/{self.total_files:,})")
                        
                except Exception as e:
                    logger.error(f"上傳失敗 {image_file.name}: {e}")
                    self.error_count += 1
            
            # 批次間短暫休息
            time.sleep(0.1)

    def upload_image(self, image_path: Path):
        """上傳單張圖片"""
        filename = image_path.name
        
        # 檢查圖片是否已存在
        try:
            self.minio_client.stat_object(self.bucket_name, filename)
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
            
            # 讀取檔案並上傳
            with open(image_path, 'rb') as f:
                file_data = f.read()
                
            data_stream = BytesIO(file_data)
            
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=data_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            self.uploaded_count += 1
            
        except Exception as e:
            logger.error(f"上傳失敗 {filename}: {e}")
            self.error_count += 1
            raise

    def check_final_status(self):
        """檢查最終狀態"""
        try:
            objects = list(self.minio_client.list_objects(self.bucket_name))
            logger.info(f"\n📊 MinIO最終狀態:")
            logger.info(f"   總圖片數量: {len(objects):,}")
            
            # 按檔案類型統計
            jpg_count = sum(1 for obj in objects if obj.object_name.lower().endswith(('.jpg', '.jpeg')))
            png_count = sum(1 for obj in objects if obj.object_name.lower().endswith('.png'))
            
            logger.info(f"   JPG/JPEG: {jpg_count:,}")
            logger.info(f"   PNG: {png_count:,}")
            
        except Exception as e:
            logger.error(f"檢查最終狀態失敗: {e}")

def main():
    """主程式"""
    uploader = BatchImageUploader(batch_size=50)  # 每批50張圖片
    
    try:
        # 初始化連接
        uploader.initialize()
        
        # 批量上傳圖片
        uploader.upload_all_images()
        
        # 檢查最終狀態
        uploader.check_final_status()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  用戶中斷上傳")
        logger.info(f"已上傳: {uploader.uploaded_count:,} 張")
        logger.info(f"已跳過: {uploader.skipped_count:,} 張")
        logger.info(f"失敗: {uploader.error_count:,} 張")
        
    except Exception as e:
        logger.error(f"❌ 上傳過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()