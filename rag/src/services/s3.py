import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from rag.src.common.settings import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self) -> None:
        self._bucket = settings.s3.S3_BUCKET
        self._client = boto3.client(
            "s3",
            region_name=settings.s3.AWS_REGION,
            aws_access_key_id=settings.s3.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.s3.AWS_SECRET_ACCESS_KEY,
        )

    def upload_invoice(self, pdf_bytes: bytes, key: str) -> str:
        """Upload invoice PDF and return the S3 object key."""
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=pdf_bytes,
                ContentType="application/pdf",
            )
            logger.info("Invoice uploaded: s3://%s/%s", self._bucket, key)
            return key
        except (BotoCoreError, ClientError) as exc:
            logger.error("Failed to upload invoice %s: %s", key, exc)
            raise

    def download_invoice(self, key: str) -> bytes:
        """Download invoice PDF by S3 object key and return raw bytes."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            data: bytes = response["Body"].read()
            logger.info("Invoice downloaded: s3://%s/%s", self._bucket, key)
            return data
        except (BotoCoreError, ClientError) as exc:
            logger.error("Failed to download invoice %s: %s", key, exc)
            raise

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary download access."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )


s3_service = S3Service()
