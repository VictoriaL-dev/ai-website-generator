import traceback
from collections.abc import AsyncGenerator, Awaitable, Callable

import anyio
import httpx
from fastapi import Request
from html_page_generator import AsyncPageGenerator

from storage import save_html_to_s3


async def generate_web_page(
    site_id: int,
    user_prompt: str,
    debug_mode: bool,
    request: Request,
    on_title_found: Callable[[str], Awaitable[None]] | None = None
) -> AsyncGenerator:
    with anyio.CancelScope(shield=True):
        try:
            generator = AsyncPageGenerator(debug_mode=debug_mode)
            title_saved = False
            client_disconnected = False

            async for chunk in generator(user_prompt=user_prompt):
                yield chunk

                print(chunk, end="", flush=True)

                if not title_saved and generator.html_page.title:
                    if on_title_found:
                        await on_title_found(generator.html_page.title)
                    title_saved = True

                if await request.is_disconnected():
                    client_disconnected = True
                    print("\nThe connection was terminated on the client side.")
                    break

            if not client_disconnected and generator.html_page.html_code:
                await save_html_to_s3(
                    s3_client=request.app.state.s3_client,
                    bucket_name=request.app.state.settings.S3.BUCKET_NAME,
                    site_id=site_id,
                    html_code=generator.html_page.html_code
                )
                print(f"\nFile with ID {site_id} has been successfully saved to bucket.")
        except httpx.HTTPStatusError as e:
            print(f"\nA third-party service returned an error: {e.response.status_code} - {e.response.text}.")
            raise
        except httpx.RequestError as e:
            print(f"\nError connecting to external server: {e}")
            raise
        except Exception:
            print("\nUnexpected error within the generator:")
            traceback.print_exc()
            raise
