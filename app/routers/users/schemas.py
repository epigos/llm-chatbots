from app.routers import common_schemas as common


class UserOutput(common.BaseModelOutput):
    """
    Schema for user response
    """

    username: str
    name: str
