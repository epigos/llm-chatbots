import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import sqlalchemy
from app.cli import fixtures


async def test_can_load_fixtures(db_session: AsyncSession) -> None:
    with open(fixtures.FIXTURES_DIR / "bots.json", encoding="utf-8") as fp:
        bots_data = json.load(fp)

    await fixtures.main()
    repo = sqlalchemy.BotRepository(db_session)
    bots = await repo.get_all()
    assert len(bots) == len(bots_data)
