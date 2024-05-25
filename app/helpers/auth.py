import typing
from datetime import timedelta

import jwt
from passlib.context import CryptContext

from app.config import settings
from app.utils import utcnow

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    Create password hash
    """
    return str(pwd_context.hash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify plain password against stored hash password
    """
    return bool(pwd_context.verify(password, hashed_password))


def create_access_token(subject: str) -> str:
    """
    Create JWT access token for the subject
    """
    to_encode: dict[str, typing.Any] = {"sub": subject}

    expire = utcnow() + timedelta(minutes=settings.access_token_expires)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Create JWT Refresh token for the subject
    """
    expire = utcnow() + timedelta(minutes=settings.refresh_token_expires)

    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_refresh_secret_key, settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, typing.Any]:
    """
    Decodes JWT access token
    """
    payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    return dict(payload)
