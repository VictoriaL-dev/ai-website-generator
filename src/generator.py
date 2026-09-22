from collections.abc import AsyncGenerator, Awaitable, Callable

import anyio
import httpx
from fastapi import Request
from html_page_generator import AsyncPageGenerator
from loguru import logger

from screenshot import create_and_save_screenshot
from storage import save_html_to_s3


async def generate_web_page(
    site_id: int,
    user_prompt: str,
    debug_mode: bool,
    request: Request,
    on_title_found: Callable[[str], Awaitable[None]] | None = None
) -> AsyncGenerator:
    logger.info(f"Starting web page generation pipeline for site {site_id}")
    settings = request.app.state.settings

    generator = AsyncPageGenerator(debug_mode=debug_mode)
    title_saved = False
    client_disconnected = False

    try:
        log_buffer = ""
        async for chunk in generator(user_prompt=user_prompt):
            yield str(chunk)

            if debug_mode and settings.LOG_LEVEL == "DEBUG":
                log_buffer += chunk
                if "\n" in log_buffer:
                    lines = log_buffer.split("\n")
                    for line in lines[:-1]:
                        if line.strip():
                            logger.debug(line)
                    log_buffer = lines[-1]

            if not title_saved and generator.html_page.title:
                if on_title_found:
                    await on_title_found(generator.html_page.title)
                    logger.info(f"Site title resolved for site {site_id}: {generator.html_page.title}")
                title_saved = True

            if await request.is_disconnected():
                client_disconnected = True
                logger.warning(f"Client disconnected early. Aborting generation for site {site_id}")
                break

        if debug_mode and settings.LOG_LEVEL == "DEBUG" and log_buffer.strip():
            logger.debug(log_buffer)
    except anyio.get_cancelled_exc_class():
        client_disconnected = True
        logger.warning(f"Task cancelled for site {site_id}")
        return
    except httpx.ReadTimeout as e:
        logger.warning(f"Read timeout for site {site_id}: {e}")
        return
    except httpx.HTTPStatusError as e:
        logger.error(f"External service returned an error for site {site_id}: {e}")
        return
    except (httpx.ConnectTimeout, httpx.ConnectError, httpx.RequestError) as e:
        logger.error(f"Network error connecting to external service for site {site_id}: {e}")
        return
    except Exception as e:
        logger.exception(f"Unexpected error within the LLM generator for site {site_id}: {e}")
        return

    if not client_disconnected and generator.html_page.html_code:
        with anyio.CancelScope(shield=True):
            logger.info(f"Generation completed. Persisting assets for site {site_id} to S3 bucket...")
            try:
                await save_html_to_s3(
                    s3_client=request.app.state.s3_client,
                    bucket_name=request.app.state.settings.S3.BUCKET_NAME,
                    site_id=site_id,
                    html_code=generator.html_page.html_code
                )
                await create_and_save_screenshot(
                    site_id=site_id,
                    html_code=generator.html_page.html_code,
                    gotenberg_client=request.app.state.gotenberg_client,
                    gotenberg_settings=request.app.state.settings.GOTENBERG,
                    s3_client=request.app.state.s3_client,
                    s3_settings=request.app.state.settings.S3,
                    database=request.app.state.database
                )
                logger.success(f"Pipeline successfully finished for site {site_id}")
            except Exception as e:
                logger.exception(f"Critical error during post-generation persistence for site {site_id}: {e}")
                return
