from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepSeekSettings(BaseModel):
    API_KEY: SecretStr
    BASE_URL: str
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
    BASE_URL: str = "http://127.0.0.1:9000"
    API_PORT: int = 9000
    MINIO_PORT: int = 9001
    ACCESS_KEY: str
    SECRET_KEY: SecretStr
    BUCKET_NAME: str = "generated-sites"
    MAX_CONNECTIONS: PositiveInt = 5
    CONNECTION_TIMEOUT: PositiveInt | PositiveFloat = 10
    READ_TIMEOUT: PositiveInt | PositiveFloat = 10

    model_config = ConfigDict(extra="forbid")


class AppSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    FRONTEND_DIR: Path = Path("frontend")

    DEEP_SEEK: DeepSeekSettings
    UNSPLASH: UnsplashSettings
    S3: S3Settings

    @property
    def project_root(self):
        return self._get_project_root()

    @classmethod
    def _get_project_root(cls):
        return Path(__file__).resolve().parent.parent

    @field_validator("FRONTEND_DIR")
    @classmethod
    def validate_frontend_dir(cls, value):
        path = Path(value)
        if not path.is_absolute():
            root = cls._get_project_root()
            return (root / path).resolve()
        return path.resolve()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )


@lru_cache
def load_settings():
    return AppSettings()
