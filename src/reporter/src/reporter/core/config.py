from typing import List, Optional

from minio import Minio
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API settings
    PROJECT_NAME: str = "flooq reporter"
    VERSION: str = "1.0.0"

    # server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # CORS settings
    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # openapi schemas
    OPENAPI_URL: Optional[str] = None
    DOCS_URL: Optional[str] = None
    REDOC_URL: Optional[str] = None

    # S3 configuration
    S3_BUCKET: str
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str
    S3_ENDPOINT_EXTERNAL_URL: Optional[str] = None
    S3_ACCESS_KEY: SecretStr
    S3_SECRET_KEY: SecretStr
    S3_SECURE: bool = False

    # AI api config
    GOOGLE_API_KEY: str

    @property
    def S3_CLIENT(self) -> Minio:
        return Minio(
            endpoint=self.S3_ENDPOINT_URL,
            access_key=self.S3_ACCESS_KEY.get_secret_value(),
            secret_key=self.S3_SECRET_KEY.get_secret_value(),
            region=self.S3_REGION,
            secure=self.S3_SECURE,
        )


settings = Settings()
