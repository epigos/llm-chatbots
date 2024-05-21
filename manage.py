import typer

from app import db, logging_config
from app.cli import setup_commands
from app.config import settings

logging_config.configure()

app = typer.Typer()

setup_commands(app)

if __name__ == "__main__":
    db.async_db.init(settings)
    app()
