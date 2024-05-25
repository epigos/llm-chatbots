import typing

import pydantic

from app.routers import common_schemas as common


class TokenOut(common.BaseOutputSchema):
    """
    Schema for Login token response
    """

    access_token: str
    refresh_token: str
    token_type: typing.Literal["bearer"] = "bearer"


class CreateUser(common.BaseInputSchema):
    """
    Schema for creating users
    """

    username: pydantic.EmailStr
    name: str
    password: str


class UserOutput(common.BaseModelOutput):
    """
    Schema for user response
    """

    username: str
    name: str
