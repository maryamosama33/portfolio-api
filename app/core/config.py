from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration, loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "Portfolio API"
    log_level: str = "INFO"

    # --- Storage ---
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "portfolio"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 60

    # --- Celery ---
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- Auth (single admin account; the portfolio has one owner) ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_username: str = "admin"
    admin_password_hash: str  # bcrypt hash, generate with `python -m scripts.hash_password`

    # --- AI providers ---
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    tavily_api_key: str | None = None

    # --- Job search ---
    job_search_location: str = "Egypt"
    job_search_domains: str = "linkedin.com,indeed.com,glassdoor.com,wuzzuf.net,wellfound.com"
    job_search_results_per_query: int = 5
    job_scoring_concurrency: int = 4

    @cached_property
    def job_search_domain_list(self) -> list[str]:
        return [d.strip() for d in self.job_search_domains.split(",") if d.strip()]


settings = Settings()
