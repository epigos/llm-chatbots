import fastapi
from fastapi import APIRouter

from app import deps
from app.routers.auth import schemas

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[fastapi.Depends(deps.get_token)]
)


@router.get("/me/")
async def get_user(
    current_user: deps.CurrentUser,
) -> schemas.UserOutput:
    """
    Endpoint to retrive current user.
    """

    return schemas.UserOutput.model_validate(current_user)
