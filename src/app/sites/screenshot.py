import httpx
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from loguru import logger

from core.env_settings import GotenbergSettings


async def generate_screenshot(
    site_id: int,
    html_code: str,
    gotenberg_client: httpx.AsyncClient,
    gotenberg_settings: GotenbergSettings
) -> bytes | None:
    """Generates a screenshot for the created website using the Gotenberg API."""
    logger.info(f"Requesting screenshot from Gotenberg for site {site_id}")
    try:
        screenshot_bytes = await ScreenshotHTMLRequest(
            index_html=html_code,
            width=gotenberg_settings.SCREENSHOT_WIDTH,
            format=gotenberg_settings.SCREENSHOT_FORMAT,
            wait_delay=gotenberg_settings.ANIMATION_TIMEOUT,
        ).asend(gotenberg_client)
        logger.success(f"Successfully generated a screenshot for site {site_id}")
        return screenshot_bytes or None
    except GotenbergServerError as e:
        logger.error(f"Gotenberg rendering engine failed for site {site_id}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error during screenshot generation for site {site_id}: {e}")
        return None
