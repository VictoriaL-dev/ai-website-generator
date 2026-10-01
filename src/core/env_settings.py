from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    PositiveFloat,
    PositiveInt,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

StrHttpUrl = Annotated[str, BeforeValidator(lambda url: str(HttpUrl(url)))]


class DeepSeekSettings(BaseModel):
    API_KEY: SecretStr
    BASE_URL: StrHttpUrl
    MODEL: str
    MAX_CONNECTIONS: PositiveInt = 5
    TIMEOUT: PositiveInt | PositiveFloat = 20

    model_config = ConfigDict(extra="forbid")


class UnsplashSettings(BaseModel):
    API_KEY: SecretStr
    MAX_CONNECTIONS: PositiveInt = 5
    TIMEOUT: PositiveInt | PositiveFloat = 20

    model_config = ConfigDict(extra="forbid")


class S3Settings(BaseModel):
    BASE_URL: StrHttpUrl = StrHttpUrl("http://127.0.0.1:9000")
    API_PORT: PositiveInt = Field(default=9000, gt=0, lt=65535)
    MINIO_PORT: PositiveInt = Field(default=9001, gt=0, lt=65535)
    ACCESS_KEY: str
    SECRET_KEY: SecretStr
    BUCKET_NAME: str = "generated-sites"
    MAX_CONNECTIONS: PositiveInt = 5
    CONNECTION_TIMEOUT: PositiveInt | PositiveFloat = 10
    READ_TIMEOUT: PositiveInt | PositiveFloat = 10

    model_config = ConfigDict(extra="forbid")


class GotenbergSettings(BaseModel):
    BASE_URL: StrHttpUrl = StrHttpUrl("https://demo.gotenberg.dev")
    SCREENSHOT_WIDTH: PositiveInt = 1280
    SCREENSHOT_FORMAT: Literal["png", "jpeg", "webp"] = "jpeg"
    MAX_CONNECTIONS: PositiveInt = 5
    SCREENSHOT_TIMEOUT: PositiveInt | PositiveFloat = 20
    ANIMATION_TIMEOUT: PositiveInt | PositiveFloat = 5

    model_config = ConfigDict(extra="forbid")


class AppSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: PositiveInt = Field(default=8000, gt=0, lt=65535)
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    FRONTEND_DIR: Path = Path("frontend")

    DEEP_SEEK: DeepSeekSettings
    UNSPLASH: UnsplashSettings
    S3: S3Settings
    GOTENBERG: GotenbergSettings

    @property
    def project_root(self) -> Path:
        return self._get_project_root()

    @classmethod
    def _get_project_root(cls) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @field_validator("FRONTEND_DIR")
    @classmethod
    def validate_frontend_dir(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            root = cls._get_project_root()
            return (root / path).resolve()
        return path.resolve()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        env_nested_delimiter="__"
    )
