from app import models


def test_can_encrypt_and_verify_password(user: models.User) -> None:
    user.set_password_hash("password")
    assert user.password != "password"

    correct = user.verify_password("password")
    assert correct is True
