import typing
from pathlib import Path

from pydantic_settings import BaseSettings
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
    db_echo: bool = False

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


settings = Settings()
