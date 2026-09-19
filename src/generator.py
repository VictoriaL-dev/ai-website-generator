import traceback
from collections.abc import AsyncGenerator, Awaitable, Callable

import anyio
import httpx
from fastapi import Request
from html_page_generator import AsyncPageGenerator


async def generate_web_page(
    user_prompt: str,
    file_path: anyio.Path,
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
                await file_path.write_text(generator.html_page.html_code, encoding="utf-8")
                print(f"\nFile '{file_path}' has been successfully saved.")
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
