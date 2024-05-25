import typing

import fastapi
from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from app import deps, exceptions, models, ports
from app.helpers import auth
from app.routers.auth import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])


async def authenticate_user(
    user_repo: ports.UserRepository, username: str, password: str
) -> models.User | None:
    """
    Fetch user from the database and authenticate it by verifying username and password.
    """
    try:
        user = await user_repo.get_by_username(username)
        if not auth.verify_password(password, user.password):
            return None
        return user
    except exceptions.DoesNotExist:
        return None


@router.post("/login/")
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, fastapi.Depends()],
    user_repo: deps.UserRepository,
) -> schemas.TokenOut:
    """
    Endpoint to login user and obtain an access token.
    """
    if not (
        user := await authenticate_user(
            user_repo, form_data.username, form_data.password
        )
    ):
        raise exceptions.AuthenticationError("Incorrect username or password")

    access_token = auth.create_access_token(user.username)
    refresh_token = auth.create_refresh_token(user.username)
    return schemas.TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: schemas.CreateUser, user_repo: deps.UserRepository
) -> schemas.UserOutput:
    """
    Endpoint to register a new user.
    """
    user = models.User(username=data.username, name=data.name)
    user.set_password_hash(data.password)
    user = await user_repo.save(user)

    return schemas.UserOutput.model_validate(user)
