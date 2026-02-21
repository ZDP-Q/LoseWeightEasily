import io
import logging
import uuid
from datetime import timedelta
from minio import Minio
from .config import get_settings

logger = logging.getLogger("loseweight.minio")


class MinIOClient:
    def __init__(self):
        settings = get_settings().minio
        self.client = Minio(
            endpoint=settings.endpoint,
            access_key=settings.access_key,
            secret_key=settings.secret_key,
            secure=settings.secure,
        )
        self.bucket_name = settings.bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """确保存储桶存在，不存在则创建。"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {e}")

    def upload_image(self, image_bytes: bytes, content_type: str = "image/jpeg") -> str:
        """上传图片并返回对象键（Object Key）。"""
        file_name = f"recognition_{uuid.uuid4().hex}.jpg"
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=io.BytesIO(image_bytes),
                length=len(image_bytes),
                content_type=content_type,
            )
            logger.info(f"Successfully uploaded image to MinIO: {file_name}")
            return file_name
        except Exception as e:
            logger.error(f"Failed to upload image to MinIO: {e}")
            raise e

    def get_presigned_url(self, object_name: str, expires_hours: int = 24) -> str:
        """生成临时的访问链接。"""
        try:
            return self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(hours=expires_hours)
            )
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return ""


# 单例对象供全局使用
minio_client = MinIOClient()
