import json
from unittest import mock
from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, ports
from app.adapters import sqlalchemy
from app.cli import fixtures


async def test_can_load_fixtures(db_session: AsyncSession) -> None:
    with open(fixtures.FIXTURES_DIR / "bots.json", encoding="utf-8") as fp:
        bots_data = json.load(fp)

    with (
        patch.object(deps, "get_embeddings"),
        patch.object(deps, "get_vector_store") as mock_get_vector_store,
    ):
        mock_get_vector_store.return_value = mock.MagicMock(spec=ports.VectorStore)
        await fixtures.main()

    repo = sqlalchemy.BotRepository(db_session)
    bots = await repo.get_all()
    assert len(bots) == len(bots_data)

    mock_get_vector_store.assert_called()
