import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False,)

    staging_dir: Path = Field(default=Path("./staging"), alias="STAGING_DIR")
    db_connections: dict[str, str] = Field(default_factory=dict, alias="DB_CONNECTIONS")
    max_result_rows: int = Field(default=1000, gt=0, le=100000,alias="MAX_RESULT_ROWS")
    max_file_size_mb: int = Field(default=100, gt=0, le=1024,alias="MAX_FILE_SIZE_MB")
    mcp_api_key: SecretStr = Field(alias="MCP_API_KEY")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    sql_allowlist_mode: Literal["read_only", "dml"] = Field(
        default="read_only", alias="SQL_ALLOWLIST_MODE"
    )
    chart_backend: Literal["plotly", "matplotlib"] = Field(
        default="plotly", alias="CHART_BACKEND"
    )

    @field_validator("db_connections", mode="before")
    @classmethod
    def parse_db_connections(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "DB_CONNECTIONS must be a valid JSON"
                ) from e
        return v

    @field_validator("staging_dir", mode="after")
    @classmethod
    def resolve_staging_dir(cls, v: Path) -> Path:
        return v.resolve()

    @model_validator(mode="after")
    def validate_staging_dir(self) -> "Settings":
        if not self.staging_dir.exists():
            self.staging_dir.mkdir(parents=True, exist_ok=True)
        if not self.staging_dir.is_dir():
            raise ValueError(f"STAGING_DIR {self.staging_dir} is not a directory")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
