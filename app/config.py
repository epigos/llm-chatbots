import typing
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    """
    Settings for this project
    """

    root_dir: Path = Path(__file__).parent.parent
    apps_dir: Path = Path(__file__).parent

    app_name: str = "llm-api"
    debug: bool = True
    log_level: str = "DEBUG"
    log_format: typing.Literal["json", "console", "colored"] = "colored"

    db_driver: str = "postgresql+asyncpg"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "password"
    db_database: str = "postgres"
    db_echo: bool = True

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    redis_url: str = "redis://localhost:6379/0"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "documents"

    @property
    def database_url(self) -> URL:
        """
        Returns database connection URI
        """
        return URL.create(
            self.db_driver,
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_database,
        )

    model_config = SettingsConfigDict(
        env_file=f"{root_dir}/.env", env_file_encoding="utf-8"
    )


settings = Settings()
