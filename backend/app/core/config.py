from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://nestmate:nestmate@localhost:5432/nestmate"

    # JWT
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 30

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # OAuth
    oauth_redirect_base: str = "http://localhost:8000"
    frontend_base: str = "http://localhost:5173"
    google_client_id: str = ""
    google_client_secret: str = ""
    wechat_appid: str = ""
    wechat_secret: str = ""

    admin_emails: str = ""

    @property
    def admin_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.admin_emails.split(",") if e.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
