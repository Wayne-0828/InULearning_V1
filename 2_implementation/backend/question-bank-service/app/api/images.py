from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.database import DatabaseManager, get_database
from app.config import settings
from minio import Minio
from minio.error import S3Error
import io
from typing import Optional

router = APIRouter(prefix="/images", tags=["images"])

def get_minio_client():
    """獲取MinIO客戶端"""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False
    )


@router.get("/{image_filename}")
async def get_image(image_filename: str):
    """獲取圖片"""
    try:
        minio_client = get_minio_client()
        
        # 檢查圖片是否存在
        try:
            minio_client.stat_object(settings.minio_bucket_name, image_filename)
        except S3Error as e:
            if e.code == 'NoSuchKey':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"圖片不存在: {image_filename}"
                )
            raise
        
        # 獲取圖片數據
        response = minio_client.get_object(settings.minio_bucket_name, image_filename)
        image_data = response.read()
        
        # 返回圖片流
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename={image_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取圖片失敗: {str(e)}"
        )


@router.get("/check/{image_filename}")
async def check_image_exists(image_filename: str):
    """檢查圖片是否存在"""
    try:
        minio_client = get_minio_client()
        
        try:
            minio_client.stat_object(settings.minio_bucket_name, image_filename)
            return {"exists": True, "filename": image_filename}
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return {"exists": False, "filename": image_filename}
            raise
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"檢查圖片失敗: {str(e)}"
        )