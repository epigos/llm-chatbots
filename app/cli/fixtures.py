import asyncio
import json
import logging
from pathlib import Path

import typer
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession

from app import db, deps, models, typings
from app.adapters import sqlalchemy
from app.config import settings

app = typer.Typer()

FIXTURES_DIR = Path(__file__).parent / "fixtures_data"

logger = logging.getLogger(__name__)


async def _load_bots(session: AsyncSession) -> None:
    with open(FIXTURES_DIR / "bots.json", encoding="utf-8") as fp:
        bots_data = json.load(fp)

    bots_repo = sqlalchemy.BotRepository(session)
    embedding = deps.get_embeddings()
    vector_store = deps.get_vector_store(embedding)

    logging.info("Loading %s bots into the database.", len(bots_data))

    for bot_data in bots_data:
        bot = models.Bot(
            name=bot_data["name"],
            welcome_message=bot_data["welcome_message"],
            avatar=bot_data["avatar"],
            bot_type=bot_data.get("bot_type") or typings.BotType.chatbot,
            data_source=bot_data.get("data_source") or typings.BotDataSource.text,
        )
        for ctx in bot_data.get("contexts") or []:
            bot.contexts.append(
                models.BotContext(role=ctx["role"], content=ctx["content"])
            )

        documents = bot_data.get("documents") or []
        for doc in documents:
            bot.documents.append(
                models.BotDocument(content=doc["content"], doc_metadata=doc["metadata"])
            )

        await bots_repo.save(bot)

        logging.info("Created bot: %s", bot)

        if not documents:
            continue

        # index bots with documents
        bot_db = await bots_repo.get_by_id(bot.id)
        await vector_store.index(bot_db)


async def _create_test_user(session: AsyncSession) -> None:
    logging.info("Creating test user.")

    user_repo = sqlalchemy.UserRepository(session)
    user = models.User(name="John Doe", username=settings.test_username)
    user.set_password_hash(settings.test_user_password)
    await user_repo.save(user)

    logging.info("Successfully created test user: %s", user)


async def _delete_tables(session: AsyncSession) -> None:
    tables = [models.User, models.BotContext, models.BotDocument, models.Bot]
    logger.info("Truncating tables: %s", tables)
    for table in tables:
        await session.execute(sql.delete(table))


async def main() -> None:
    """
    Main entry point to load fixtures
    """
    async with db.async_db.session() as session:
        await _delete_tables(session)
        await _create_test_user(session)
        await _load_bots(session)


@app.command("load", help="Populate db with fixtures")
def load() -> None:
    """
    Command to populate db with fixtures
    """
    asyncio.run(main())
