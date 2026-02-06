from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="allow",
    )

    app_name: str = Field(default="Data Analyst Agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    request_id_header: str = Field(default="X-Request-ID", alias="REQUEST_ID_HEADER")
    auth_token: str = Field(default="", alias="AUTH_TOKEN")

    database_url: str = Field(default="sqlite:///./data.db", alias="DATABASE_URL")
    sql_engine: str = Field(default="clickhouse", alias="SQL_ENGINE")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_strict_json: bool = Field(default=True, alias="LLM_STRICT_JSON")
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    dashscope_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1", alias="DASHSCOPE_BASE_URL"
    )
    dashscope_model: str = Field(default="", alias="DASHSCOPE_MODEL")

    # ClickHouse
    clickhouse_url: str = Field(default="http://localhost:8123", alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(default="", alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field(default="", alias="CLICKHOUSE_PASSWORD")
    clickhouse_database: str = Field(default="default", alias="CLICKHOUSE_DATABASE")

    uploads_dir: str = Field(default="./data/uploads", alias="UPLOADS_DIR")
    max_upload_mb: int = Field(default=50, alias="MAX_UPLOAD_MB")

    # Governance and safety thresholds
    min_group_size: int = Field(default=50, alias="MIN_GROUP_SIZE")
    max_scan_bytes: int = Field(default=5_000_000_000, alias="MAX_SCAN_BYTES")
    default_sample_rate: float = Field(default=1.0, alias="DEFAULT_SAMPLE_RATE")
    allow_detail_export: bool = Field(default=False, alias="ALLOW_DETAIL_EXPORT")
    rate_limit_rps: int = Field(default=10, alias="RATE_LIMIT_RPS")
    data_preview_limit: int = Field(default=50, alias="DATA_PREVIEW_LIMIT")
    task_history_limit: int = Field(default=50, alias="TASK_HISTORY_LIMIT")

    def cors_origin_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
