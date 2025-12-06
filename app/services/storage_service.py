import boto3
from botocore.exceptions import ClientError
from config import settings
from utils.logger import logger

def get_s3_client():
    try:
        return boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    except Exception as e:
        logger.error(f"S3 Client initialization failed: {e}")
        return None

s3_client = get_s3_client()

def upload_to_s3(key: str, body: bytes, content_type: str):
    if not s3_client:
        return False, "S3 client not initialized"

    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=body,
            ContentType=content_type
        )
        return True, None
    except ClientError as e:
        return False, str(e)

