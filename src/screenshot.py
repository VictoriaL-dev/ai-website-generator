from urllib.parse import urljoin

import httpx
from aiobotocore.client import AioBaseClient
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from loguru import logger

from env_settings import GotenbergSettings, S3Settings
from storage import save_screenshot_to_s3


async def create_and_save_screenshot(
    site_id: int,
    html_code: str,
    gotenberg_client: httpx.AsyncClient,
    gotenberg_settings: GotenbergSettings,
    s3_client: AioBaseClient,
    s3_settings: S3Settings,
    database: dict
) -> None:
    """Generates a screenshot via Gotenberg API and saves it to MinIO S3."""
    logger.info(f"Requesting screenshot from Gotenberg for site {site_id}")
    try:
        screenshot_bytes = await ScreenshotHTMLRequest(
            index_html=html_code,
            width=gotenberg_settings.SCREENSHOT_WIDTH,
            format=gotenberg_settings.SCREENSHOT_FORMAT,
            wait_delay=gotenberg_settings.ANIMATION_TIMEOUT,
        ).asend(gotenberg_client)

        await save_screenshot_to_s3(
            s3_client=s3_client,
            bucket_name=s3_settings.BUCKET_NAME,
            site_id=site_id,
            screenshot_bytes=screenshot_bytes,
            screenshot_format=gotenberg_settings.SCREENSHOT_FORMAT
        )

        screenshot_key = f"screenshot_{site_id}.{gotenberg_settings.SCREENSHOT_FORMAT}"
        if site_id in database:
            base_url = s3_settings.BASE_URL
            file_path = f"{s3_settings.BUCKET_NAME}/{screenshot_key}"
            full_file_path = urljoin(base_url, file_path)

            database[site_id]["screenshot_url"] = full_file_path
            logger.info(f"Screenshot URL updated for site {site_id}")
    except GotenbergServerError as e:
        logger.error(f"Gotenberg rendering engine failed for site {site_id}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during screenshot processing for site {site_id}: {e}")
