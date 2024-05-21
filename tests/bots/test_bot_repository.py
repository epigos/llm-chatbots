import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import sqlalchemy


@pytest.mark.asyncio
async def test_bot_crud(db_session: AsyncSession, bot) -> None:
    repo = sqlalchemy.BotRepository(db_session)

    bot_db = await repo.save(bot)
    assert bot.id == bot_db.id
    assert bot.name == bot_db.name
    assert bot.welcome_message == bot_db.welcome_message

    get_bot = await repo.get_by_id(bot.id)
    assert get_bot == bot_db

    for_update = await repo.get_for_update(bot.id)
    for_update.name = "new name"
    updated_bot = await repo.save(for_update)
    assert updated_bot.name == "new name"

    await repo.delete(updated_bot)

    with pytest.raises(HTTPException) as excinfo:
        await repo.get_by_id(bot.id)
        assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_bot_get_all(db_session: AsyncSession, bot_factory) -> None:
    repo = sqlalchemy.BotRepository(db_session)
    bots = bot_factory.create_batch(10)
    for bot in bots:
        await repo.save(bot)

    bot_lists = await repo.get_all()
    assert len(bot_lists) == len(bots)
