import traceback
from urllib.parse import urljoin

import httpx
from aiobotocore.client import AioBaseClient
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest

from env_settings import GotenbergSettings, S3Settings


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
    try:
        screenshot_bytes = await ScreenshotHTMLRequest(
            index_html=html_code,
            width=gotenberg_settings.SCREENSHOT_WIDTH,
            format=gotenberg_settings.SCREENSHOT_FORMAT,
            wait_delay=gotenberg_settings.ANIMATION_TIMEOUT,
        ).asend(gotenberg_client)

        screenshot_key = f"screenshot_{site_id}.{gotenberg_settings.SCREENSHOT_FORMAT}"

        await s3_client.put_object(
            Bucket=s3_settings.BUCKET_NAME,
            Key=screenshot_key,
            Body=screenshot_bytes,
            ContentType=f"image/{gotenberg_settings.SCREENSHOT_FORMAT}",
        )

        if site_id in database:
            base_url = s3_settings.BASE_URL
            file_path = f"{s3_settings.BUCKET_NAME}/{screenshot_key}"
            full_file_path = urljoin(base_url, file_path)

            database[site_id]["screenshot_url"] = full_file_path

        print(f"Screenshot for site with ID {site_id} successfully saved to S3.")
    except GotenbergServerError as e:
        print(f"Gotenberg returned an error while rendering screenshot {site_id}: {e}")
    except Exception as e:
        print(f"Error processing screenshot for {site_id}: {e}")
        traceback.print_exc()
