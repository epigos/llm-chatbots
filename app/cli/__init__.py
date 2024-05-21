import typer

from .fixtures import app as fixture_app


def setup_commands(app: typer.Typer) -> None:
    """Setup app commands"""
    app.add_typer(fixture_app, name="fixtures")
