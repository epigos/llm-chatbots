import asyncio
import json
import logging
from pathlib import Path

import typer
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, models
from app.adapters import sqlalchemy

app = typer.Typer()

FIXTURES_DIR = Path(__file__).parent / "fixtures_data"

logger = logging.getLogger(__name__)


async def _load_bots(session: AsyncSession) -> None:
    with open(FIXTURES_DIR / "bots.json", encoding="utf-8") as fp:
        bots_data = json.load(fp)

    bots_repo = sqlalchemy.BotRepository(session)

    logging.info("Loading %s bots into the database.", len(bots_data))
    for bot_data in bots_data:
        bot = models.Bot(
            name=bot_data["name"],
            welcome_message=bot_data["welcome_message"],
            avatar=bot_data["avatar"],
        )
        for ctx in bot_data["contexts"]:
            bot.contexts.append(
                models.BotContext(role=ctx["role"], content=ctx["content"])
            )

        await bots_repo.save(bot)


async def _delete_tables(session: AsyncSession) -> None:
    tables = [models.BotContext, models.Bot]
    logger.info("Truncating tables: %s", tables)
    for table in tables:
        await session.execute(sql.delete(table))


async def main() -> None:
    """
    Main entry point to load fixtures
    """
    async with db.async_db.session() as session:
        await _delete_tables(session)
        await _load_bots(session)


@app.command("load", help="Populate db with fixtures")
def load() -> None:
    """
    Command to populate db with fixtures
    """
    asyncio.run(main())
