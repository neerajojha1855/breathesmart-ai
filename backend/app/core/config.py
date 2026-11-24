import os

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "BreatheSmart API"
    API_PREFIX: str = "/api/v1"
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = ""
    DATABASE_URL_UNPOOLED: str | None = None
    NEON_BRANCH: str = "production"

    # Auth & Sessions
    SESSION_SECRET_KEY: str = "insecure-secret-key-change-in-production"
    SESSION_LIFETIME_SECONDS: int = 86400
    SESSION_COOKIE_NAME: str = "breathe_smart_session"

    # AI Provider
    GROQ_API_KEY: str | None = None
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"
    AI_REQUEST_TIMEOUT_SECONDS: int = 60
    AI_MAX_RETRIES: int = 2

    @staticmethod
    def _normalize_async_database_url(raw_url: str) -> str:
        """Convert Postgres URI to asyncpg format and strip unsupported query params."""
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        url = make_url(raw_url)
        query = dict(url.query)
        # asyncpg does not support channel_binding
        query.pop("channel_binding", None)
        # asyncpg expects ssl=require instead of sslmode
        if "sslmode" in query and "ssl" not in query:
            query["ssl"] = query.pop("sslmode")

        # render_as_string with hide_password=False prevents masking password with '***'
        return url.set(query=query).render_as_string(hide_password=False)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        raw_url = (
            (self.DATABASE_URL or os.getenv("DATABASE_URL", ""))
            .strip()
            .strip("'")
            .strip('"')
        )
        if not raw_url:
            raise ValueError(
                "DATABASE_URL is not set. Please ensure DATABASE_URL is defined in backend/.env"
            )
        return self._normalize_async_database_url(raw_url)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ASYNC_DATABASE_URL_UNPOOLED(self) -> str:
        raw_val = (
            self.DATABASE_URL_UNPOOLED
            or self.DATABASE_URL
            or os.getenv("DATABASE_URL_UNPOOLED", "")
        )
        raw_url = (raw_val or "").strip().strip("'").strip('"')
        return self._normalize_async_database_url(raw_url)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SYNC_DATABASE_URL_UNPOOLED(self) -> str:
        raw_val = (
            self.DATABASE_URL_UNPOOLED
            or self.DATABASE_URL
            or os.getenv("DATABASE_URL_UNPOOLED", "")
        )
        raw_url = (raw_val or "").strip().strip("'").strip('"')
        if raw_url.startswith("postgresql+asyncpg://"):
            raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return raw_url

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
