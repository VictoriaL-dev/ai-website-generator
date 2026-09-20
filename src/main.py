import random
from contextlib import asynccontextmanager

import aioboto3
import httpx
import uvicorn
from aiobotocore.config import AioConfig
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from api_models import (
    CreateSiteRequest,
    GeneratedSitesResponse,
    SiteGenerationRequest,
    SiteResponse,
    UserDetailsResponse,
)
from env_settings import load_settings
from generator import generate_web_page
from storage import create_site_record, ensure_bucket_exists, get_all_sites, update_site_title

loaded_settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = loaded_settings
    app.state.database = {}

    settings = app.state.settings

    s3_config = AioConfig(
        s3={"addressing_style": "path"},
        max_pool_connections=settings.S3.MAX_CONNECTIONS,
        connect_timeout=settings.S3.CONNECTION_TIMEOUT,
        read_timeout=settings.S3.READ_TIMEOUT
    )
    s3_session = aioboto3.Session(
        aws_access_key_id=settings.S3.ACCESS_KEY,
        aws_secret_access_key=settings.S3.SECRET_KEY.get_secret_value()
    )

    async with (
        s3_session.client(
            service_name="s3",
            endpoint_url=settings.S3.BASE_URL,
            config=s3_config
        ) as s3_client,
        AsyncUnsplashClient.setup(
            unsplash_client_id=settings.UNSPLASH.API_KEY.get_secret_value(),
            limits=httpx.Limits(max_connections=settings.UNSPLASH.MAX_CONNECTIONS),
            timeout=httpx.Timeout(timeout=settings.UNSPLASH.TIMEOUT)
        ) as unsplash_client,
        AsyncDeepseekClient.setup(
            deepseek_api_key=settings.DEEP_SEEK.API_KEY.get_secret_value(),
            deepseek_base_url=settings.DEEP_SEEK.BASE_URL,
            deepseek_model=settings.DEEP_SEEK.MODEL,
            limits=httpx.Limits(max_connections=settings.DEEP_SEEK.MAX_CONNECTIONS),
            timeout=httpx.Timeout(timeout=settings.DEEP_SEEK.TIMEOUT)
        ) as deepseek_client,
        httpx.AsyncClient(
            base_url=settings.GOTENBERG.BASE_URL,
            limits=httpx.Limits(max_connections=settings.GOTENBERG.MAX_CONNECTIONS),
            timeout=httpx.Timeout(timeout=settings.GOTENBERG.SCREENSHOT_TIMEOUT)
        ) as gotenberg_client,
    ):
        app.state.s3_client = s3_client
        app.state.unsplash_client = unsplash_client
        app.state.deepseek_client = deepseek_client
        app.state.gotenberg_client = gotenberg_client

        await ensure_bucket_exists(s3_client=s3_client, bucket_name=settings.S3.BUCKET_NAME)

        yield


app = FastAPI(
    title="AI Website Generator",
    description="AI-powered website generator built with FastAPI",
    lifespan=lifespan
)


@app.get(
    "/users/me",
    tags=["Users"],
    summary="Retrieve user credentials",
    response_description="User credentials",
    response_model=UserDetailsResponse,
)
async def get_user():
    mock_user_data = {
        "profileId": 1,
        "username": "user123",
        "email": "example@example.com",
        "isActive": True,
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2026-09-15T18:29:56+00:00",
    }
    return mock_user_data


@app.post(
    "/sites/create",
    tags=["Sites"],
    summary="Create a new website from a user prompt",
    response_description="Generated website data",
    response_model=SiteResponse
)
async def create_site(payload: CreateSiteRequest, request: Request):
    settings = request.app.state.settings
    database = request.app.state.database

    site_id = random.randint(1, 100000)
    title = payload.title or "Generated Website"

    new_site = await create_site_record(
        s3_settings=settings.S3,
        site_id=site_id,
        title=title,
        prompt=payload.prompt,
        database=database
    )
    return new_site


@app.post(
    "/sites/{site_id}/generate",
    tags=["Sites"],
    summary="Generate a website with AI stream",
    response_description="Chunks of HTML code from the generated website",
)
async def generate_site(site_id: int, payload: SiteGenerationRequest, request: Request):
    settings = request.app.state.settings
    database = request.app.state.database

    site = database.get(site_id)
    if not site:
        return JSONResponse(
            content={"status_code": 404, "detail": "Not Found"},
            status_code=404
        )

    async def handle_title(generated_title: str):
        update_site_title(database=database, site_id=site_id, title=generated_title)

    return StreamingResponse(
        generate_web_page(
            site_id=site_id,
            user_prompt=payload.prompt,
            debug_mode=settings.DEBUG,
            request=request,
            on_title_found=handle_title
        ),
        media_type="text/plain; charset=utf-8"
    )


@app.get(
    "/sites/my",
    tags=["Sites"],
    summary="Get all websites generated by the current user",
    response_description="User-generated websites",
    response_model=GeneratedSitesResponse
)
async def get_user_sites(request: Request):
    database = request.app.state.database
    sites = get_all_sites(database=database)
    return {"sites": sites}


@app.get(
    "/sites/{site_id}",
    tags=["Sites"],
    summary="Get details of a specific generated website",
    response_description="HTML code of the generated website",
    response_model=SiteResponse
)
async def get_site_by_id(site_id: int, request: Request):
    database = request.app.state.database

    site = database.get(site_id)
    if not site:
        return JSONResponse(
            content={"status_code": 404, "detail": "Not Found"},
            status_code=404
        )
    return site


app.mount("/assets", StaticFiles(directory=loaded_settings.FRONTEND_DIR / "assets"), name="assets")
app.mount("/", StaticFiles(directory=loaded_settings.FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=loaded_settings.HOST,
        port=loaded_settings.PORT,
        reload=loaded_settings.DEBUG
    )
