import time
from contextlib import asynccontextmanager

import aioboto3
import httpx
import uvicorn
from aiobotocore.config import AioConfig
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient
from loguru import logger

from app.sites.router import router as sites_router
from app.users.router import router as users_router
from core.env_settings import AppSettings
from core.logging_config import init_logging, shutdown_logging
from storage import ensure_bucket_exists

current_settings = AppSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = current_settings
    app.state.database = {}

    settings = app.state.settings

    init_logging(
        project_root=settings.project_root,
        folder_name="logs",
        log_file_name="app.log",
        log_level=settings.LOG_LEVEL
    )

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

        logger.info("Application started successfully")

        yield

        logger.info("Application was shutdown successfully")
        shutdown_logging()


app = FastAPI(
    title="AI Website Generator",
    description="AI-powered website generator built with FastAPI",
    lifespan=lifespan
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs all the application's HTTP requests and responses."""
    start_time = time.time()
    path = request.url.path
    method = request.method

    logger.info(f"HTTP Request: {method} {path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"HTTP Response: {method} {path} | Status: {response.status_code} | Time: {process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"HTTP Failed: {method} {path} | Error: {str(e)} | Time: {process_time:.2f}s")
        raise


app.include_router(users_router)
app.include_router(sites_router)

app.mount("/assets", StaticFiles(directory=current_settings.FRONTEND_DIR / "assets"), name="assets")
app.mount("/", StaticFiles(directory=current_settings.FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=current_settings.HOST,
        port=current_settings.PORT,
        reload=current_settings.DEBUG
    )
