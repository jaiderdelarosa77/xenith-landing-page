"""Utilidades core del backend (`config`)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / '.env'),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_name: str = 'Xenith API'
    app_env: str = 'development'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    api_prefix: str = '/v1'
    auto_migrate_on_start: bool = True

    database_url: str

    jwt_algorithm: str = 'HS256'
    jwt_access_secret: str
    jwt_refresh_secret: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    rfid_api_key: str = 'rfid-secret-key'
    resend_api_key: str | None = None
    emails_from: str = 'XENITH <onboarding@resend.dev>'
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket_name: str | None = None
    r2_public_url: str | None = None
    r2_endpoint: str | None = None
    r2_region: str = 'auto'
    r2_products_prefix: str = 'products'

    access_cookie_name: str = 'access_token'
    refresh_cookie_name: str = 'refresh_token'
    cookie_secure: bool = False
    cookie_samesite: str = 'lax'
    cookie_domain: str | None = None

    cors_origins: str = 'http://localhost:3000'

    superadmin_email: str = 'camilo.vargas@xenith.com.co'
    superadmin_password: str | None = None
    superadmin_name: str = 'Superadmin'
    superadmin_force_password_on_start: bool = False
    rate_limit_login_max: int = 5
    rate_limit_login_window_seconds: int = 900

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]


settings = Settings()
