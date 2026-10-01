from urllib.parse import urljoin

import httpx
from aiobotocore.client import AioBaseClient

from app.sites.screenshot import generate_screenshot
from core.env_settings import AppSettings
from storage import save_screenshot_to_s3, update_screenshot_url


async def process_screenshot(
    site_id: int,
    html_code: str,
    settings: AppSettings,
    s3_client: AioBaseClient,
    gotenberg_client: httpx.AsyncClient,
    database: dict
):
    """Generates a screenshot via Gotenberg API and saves it to S3 bucket."""
    screenshot_bytes = await generate_screenshot(
        site_id=site_id,
        html_code=html_code,
        gotenberg_client=gotenberg_client,
        gotenberg_settings=settings.GOTENBERG,
    )

    if screenshot_bytes:
        screenshot_key = f"screenshot_{site_id}.{settings.GOTENBERG.SCREENSHOT_FORMAT}"

        await save_screenshot_to_s3(
            s3_client=s3_client,
            bucket_name=settings.S3.BUCKET_NAME,
            screenshot_key=screenshot_key,
            screenshot_bytes=screenshot_bytes,
            screenshot_format=settings.GOTENBERG.SCREENSHOT_FORMAT
        )

        if site_id in database:
            base_url = settings.S3.BASE_URL
            file_path = f"{settings.S3.BUCKET_NAME}/{screenshot_key}"
            full_file_path = urljoin(base_url, file_path)

            update_screenshot_url(
                database=database,
                site_id=site_id,
                screenshot_url=full_file_path,
            )
