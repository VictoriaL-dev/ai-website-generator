from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError
from loguru import logger


async def ensure_bucket_exists(s3_client: AioBaseClient, bucket_name: str) -> None:
    """Checks for the existence of a bucket at startup."""
    try:
        await s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        logger.critical(f"Bucket {bucket_name} not found")
        raise RuntimeError(f"Bucket {bucket_name} not found")


async def save_html_to_s3(s3_client: AioBaseClient, bucket_name: str, site_id: int, html_code: str) -> str | None:
    """Uploads a file with the `text/html` type to a bucket."""
    site_key = f"site_{site_id}.html"
    try:
        await s3_client.put_object(
            Bucket=bucket_name,
            Key=site_key,
            Body=html_code.encode("utf-8"),
            ContentType="text/html",
            ContentEncoding="utf-8"
        )
        logger.success(f"{site_key} has been successfully saved to {bucket_name} bucket")
        return site_key
    except ClientError as e:
        logger.error(f"Failed to put {site_key} into {bucket_name} bucket: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error saving {site_key} to {bucket_name} bucket: {e}")
        return None


async def save_screenshot_to_s3(
    s3_client: AioBaseClient,
    bucket_name: str,
    site_id: int,
    screenshot_bytes: bytes,
    screenshot_format: str
) -> str | None:
    """Uploads a screenshot file to a bucket."""
    screenshot_key = f"screenshot_{site_id}.{screenshot_format}"
    try:
        await s3_client.put_object(
            Bucket=bucket_name,
            Key=screenshot_key,
            Body=screenshot_bytes,
            ContentType=f"image/{screenshot_format}"
        )
        logger.success(f"{screenshot_key} successfully saved to {bucket_name} bucket")
        return screenshot_key
    except ClientError as e:
        logger.error(f"Failed to put {screenshot_key} into {bucket_name} bucket: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error saving {screenshot_key} to {bucket_name} bucket: {e}")
        return None
