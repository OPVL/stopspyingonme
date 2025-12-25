"""Environment-specific configuration classes."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Base settings class."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # App Config
    app_name: str = "Stop Spying On Me"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Logging Config
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "human"] = Field(default="json", alias="LOG_FORMAT")

    # Database - Allow both PostgreSQL and SQLite URLs
    database_url: str = Field(..., alias="DATABASE_URL")
    db_pool_size: int = Field(default=5, ge=1, le=10)  # shared hosting

    @field_validator("database_url")
    @classmethod
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
    session_samesite: Literal["lax", "strict", "none"] = "lax"

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


class DevelopmentSettings(BaseAppSettings):
    """Development environment settings."""

    debug: bool = True
    log_level: str = "DEBUG"
    log_format: Literal["json", "human"] = "human"
    session_secure: bool = False  # Allow HTTP in development

    # Development database defaults
    database_url: str = Field(
        default="sqlite+aiosqlite:///./dev.db", alias="DATABASE_URL"
    )

    # Development SMTP defaults (use local testing)
    relay_host: str = Field(default="localhost", alias="RELAY_HOST")
    relay_port: int = Field(default=1025, alias="RELAY_PORT")  # MailHog
    relay_user: str = Field(default="dev@localhost", alias="RELAY_USER")
    relay_password: str = Field(default="dev-password", alias="RELAY_PASSWORD")
    relay_use_tls: bool = Field(default=False, alias="RELAY_USE_TLS")

    from_email: str = Field(default="dev@localhost", alias="FROM_EMAIL")


class TestingSettings(BaseAppSettings):
    """Testing environment settings."""

    debug: bool = False
    log_level: str = "WARNING"  # Reduce noise in tests
    log_format: Literal["json", "human"] = "human"

    # Always use in-memory SQLite for tests
    database_url: str = "sqlite+aiosqlite:///:memory:"

    # Test SMTP settings
    relay_host: str = "smtp.example.com"
    relay_user: str = "test@example.com"
    relay_password: str = "test-password"
    from_email: str = "test@example.com"

    # Shorter timeouts for faster tests
    magic_link_ttl: int = 60  # 1 minute
    session_max_age: int = 3600  # 1 hour


class StagingSettings(BaseAppSettings):
    """Staging environment settings."""

    debug: bool = False
    log_level: str = "INFO"
    log_format: Literal["json", "human"] = "json"

    # Staging should use secure cookies
    session_secure: bool = True

    # Staging WebAuthn settings
    webauthn_rp_id: str = Field(
        default="staging.yourdomain.com", alias="WEBAUTHN_RP_ID"
    )
    webauthn_origin: str = Field(
        default="https://staging.yourdomain.com", alias="WEBAUTHN_ORIGIN"
    )


class ProductionSettings(BaseAppSettings):
    """Production environment settings."""

    debug: bool = False
    log_level: str = "INFO"
    log_format: Literal["json", "human"] = "json"

    # Production security settings
    session_secure: bool = True
    session_samesite: Literal["lax", "strict", "none"] = "strict"

    # Conservative connection pooling for shared hosting
    db_pool_size: int = 3

    # Production WebAuthn settings
    webauthn_rp_id: str = Field(default="yourdomain.com", alias="WEBAUTHN_RP_ID")
    webauthn_origin: str = Field(
        default="https://yourdomain.com", alias="WEBAUTHN_ORIGIN"
    )


def get_settings_for_environment(env: str) -> BaseAppSettings:
    """Get settings class for the specified environment."""
    env = env.lower()

    if env == "development":
        return DevelopmentSettings()  # type: ignore[call-arg]
    elif env == "testing":
        return TestingSettings()  # type: ignore[call-arg]
    elif env == "staging":
        return StagingSettings()  # type: ignore[call-arg]
    elif env == "production":
        return ProductionSettings()  # type: ignore[call-arg]
    else:
        # Default to base settings
        return BaseAppSettings()  # type: ignore[call-arg]
