from collections.abc import AsyncGenerator

import anyio
import httpx
from aiobotocore.client import AioBaseClient
from fastapi import Request
from html_page_generator import AsyncPageGenerator
from loguru import logger

from app.sites.services import process_screenshot, update_site_artifacts
from core.env_settings import AppSettings
from storage import save_html_to_s3


async def generate_web_page(
    db: dict,
    s3_client: AioBaseClient,
    gotenberg_client: httpx.AsyncClient,
    settings: AppSettings,
    request: Request,
    site_id: int,
    user_prompt: str
) -> AsyncGenerator:
    """Generates a website page and yields its code chunks."""
    logger.info(f"Starting web page generation pipeline for site_{site_id}")

    debug_mode = settings.DEBUG
    log_level = settings.LOG_LEVEL

    title_saved = False
    client_disconnected = False
    log_buffer = ""

    site_title = ""
    site_html_code = ""

    try:
        generator = AsyncPageGenerator(debug_mode=debug_mode)

        async for chunk in generator(user_prompt=user_prompt):
            yield str(chunk)

            if debug_mode and log_level == "DEBUG":
                log_buffer += str(chunk)
                if "\n" in log_buffer:
                    lines = log_buffer.split("\n")
                    for line in lines[:-1]:
                        if line.strip():
                            logger.debug(line)
                    log_buffer = lines[-1]

            if not title_saved and generator.html_page.title:
                site_title = generator.html_page.title
                title_saved = True

            if await request.is_disconnected():
                client_disconnected = True
                logger.warning(f"Client disconnected early. Aborting generation for site_{site_id}")
                break

        site_html_code = generator.html_page.html_code

        if debug_mode and log_level == "DEBUG" and log_buffer.strip():
            logger.debug(log_buffer)
    except anyio.get_cancelled_exc_class():
        client_disconnected = True
        logger.warning(f"Task cancelled for site_{site_id}")
        return
    except httpx.ReadTimeout as e:
        logger.warning(f"Read timeout for site_{site_id}: {e}")
        return
    except httpx.HTTPStatusError as e:
        logger.error(f"External service returned an error for site_{site_id}: {e}")
        return
    except (httpx.ConnectTimeout, httpx.ConnectError, httpx.RequestError) as e:
        logger.error(f"Network error connecting to external service for site_{site_id}: {e}")
        return
    except Exception as e:
        logger.exception(f"Unexpected error within the generator for site_{site_id}: {e}")
        return

    if not client_disconnected and site_html_code:
        with anyio.CancelScope(shield=True):
            logger.info(f"Website generation completed. Persisting assets for site_{site_id} to a bucket")
            try:
                site_key = await save_html_to_s3(
                    s3_client=s3_client,
                    bucket_name=settings.S3.BUCKET_NAME,
                    site_id=site_id,
                    html_code=site_html_code
                )
                screenshot_key = await process_screenshot(
                    gotenberg_client=gotenberg_client,
                    s3_client=s3_client,
                    settings=settings,
                    site_id=site_id,
                    html_code=site_html_code
                )
                update_site_artifacts(
                    db=db,
                    s3_settings=settings.S3,
                    site_id=site_id,
                    site_title=site_title,
                    site_key=site_key,
                    screenshot_key=screenshot_key
                )
                logger.success(f"Pipeline successfully finished for site_{site_id}")
            except Exception as e:
                logger.exception(f"Error during post-generation persistence for site_{site_id}: {e}")
                return
