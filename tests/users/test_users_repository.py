import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import exceptions, models
from app.adapters import sqlalchemy


@pytest.mark.asyncio
async def test_user_crud(db_session: AsyncSession, user: models.User) -> None:
    repo = sqlalchemy.UserRepository(db_session)
    user.set_password_hash("passward")

    user_db = await repo.save(user)
    assert user.id == user_db.id
    assert user.name == user_db.name
    assert user.username == user_db.username

    get_user = await repo.get_by_username(user.username)
    assert get_user == user_db

    for_update = await repo.get_for_update(user.id)
    for_update.name = "new name"
    updated_user = await repo.save(for_update)
    assert updated_user.name == "new name"

    await repo.delete(updated_user)

    with pytest.raises(exceptions.DoesNotExist, match="User does not exist"):
        await repo.get_by_username(user.username)
