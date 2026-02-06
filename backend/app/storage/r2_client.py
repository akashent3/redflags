"""Cloudflare R2 storage client for PDF file management."""

import logging
from io import BytesIO
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class R2Client:
    """Client for interacting with Cloudflare R2 storage."""

    def __init__(self):
        """Initialize R2 client with credentials from settings."""
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",  # R2 uses 'auto' for region
        )
        self.bucket_name = settings.r2_bucket_name
        logger.info(f"R2 client initialized for bucket: {self.bucket_name}")

    def upload_file(
        self, file_content: bytes, object_key: str, content_type: str = "application/pdf"
    ) -> str:
        """
        Upload a file to R2 storage.

        Args:
            file_content: File content as bytes
            object_key: Unique key for the object (e.g., "reports/2023/RELIANCE_FY2023.pdf")
            content_type: MIME type of the file

        Returns:
            Public URL of the uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            file_obj = BytesIO(file_content)
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
            logger.info(f"Successfully uploaded file to R2: {object_key}")

            # Construct public URL
            public_url = f"{settings.r2_public_url}/{object_key}"
            return public_url

        except ClientError as e:
            logger.error(f"Failed to upload file to R2: {e}")
            raise Exception(f"R2 upload failed: {str(e)}")

    def download_file(self, object_key: str) -> bytes:
        """
        Download a file from R2 storage.

        Args:
            object_key: Unique key of the object to download

        Returns:
            File content as bytes

        Raises:
            Exception: If download fails
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
            file_content = response["Body"].read()
            logger.info(f"Successfully downloaded file from R2: {object_key}")
            return file_content

        except ClientError as e:
            logger.error(f"Failed to download file from R2: {e}")
            raise Exception(f"R2 download failed: {str(e)}")

    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from R2 storage.

        Args:
            object_key: Unique key of the object to delete

        Returns:
            True if deletion successful

        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Successfully deleted file from R2: {object_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file from R2: {e}")
            raise Exception(f"R2 deletion failed: {str(e)}")

    def file_exists(self, object_key: str) -> bool:
        """
        Check if a file exists in R2 storage.

        Args:
            object_key: Unique key of the object to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

    def get_file_size(self, object_key: str) -> Optional[int]:
        """
        Get the size of a file in R2 storage.

        Args:
            object_key: Unique key of the object

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            return response["ContentLength"]
        except ClientError as e:
            logger.error(f"Failed to get file size from R2: {e}")
            return None

    def generate_presigned_url(
        self, object_key: str, expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary file access.

        Args:
            object_key: Unique key of the object
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL, or None if generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None


# Singleton instance
r2_client = R2Client()
