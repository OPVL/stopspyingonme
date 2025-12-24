from functools import lru_cache

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    # App Config
    app_name: str = "Stop Spying On Me"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)

    # Database - Allow both PostgreSQL and SQLite URLs
    database_url: str = Field(..., alias="DATABASE_URL")
    db_pool_size: int = Field(default=5, ge=1, le=10)  # shared hosting

    @field_validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Allow PostgreSQL and SQLite URLs."""
        if not (v.startswith(("postgresql", "sqlite"))):
            raise ValueError("Database URL must be PostgreSQL or SQLite")
        return v

    # SMTP Relay
    relay_host: str = Field(..., alias="RELAY_HOST")
    relay_port: int = Field(default=587, alias="RELAY_PORT")
    relay_user: str = Field(..., alias="RELAY_USER")
    relay_password: str = Field(..., alias="RELAY_PASSWORD")
    relay_use_tls: bool = Field(default=True, alias="RELAY_USE_TLS")

    # Session Config
    session_cookie_name: str = "session"
    session_max_age: int = 86400 * 7  # 7 days
    session_secure: bool = True
    session_httponly: bool = True
    session_samesite: str = "lax"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour

    # Email Config
    from_email: str = Field(..., alias="FROM_EMAIL")
    magic_link_ttl: int = 900  # 15 minutes

    # WebAuthn
    webauthn_rp_id: str = Field(
        default="localhost",
        alias="WEBAUTHN_RP_ID",
    )
    webauthn_rp_name: str = Field(
        default="Stop Spying On Me",
        alias="WEBAUTHN_RP_NAME",
    )
    webauthn_origin: str = Field(
        default="http://localhost:8000",
        alias="WEBAUTHN_ORIGIN",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
