import io
import typing
import uuid

import fastapi
from fastapi import APIRouter, Form, UploadFile, status

from app import deps
from app.routers.uploads import schemas

router = APIRouter(
    prefix="/uploads", tags=["Uploads"], dependencies=[fastapi.Depends(deps.get_token)]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_upload_file(
    file: UploadFile,
    file_storage: deps.FileStorage,
    bot_id: typing.Annotated[uuid.UUID, Form()],
    bot_repo: deps.BotRepository,
) -> schemas.FileUploadOutput:
    """
    Upload a file and return the metadata about the uploaded file.
    """
    file_name = file.filename
    data = schemas.UploadFileInput.model_validate({"filename": file_name})

    bot = await bot_repo.get_by_id(bot_id)

    location = f"{bot.id}/{uuid.uuid4()}{data.extension}"

    contents = await file.read()
    with io.BytesIO(contents) as buffer:
        file_storage.upload(location, buffer)

    return schemas.FileUploadOutput(
        location=location, content_type=file.content_type, filename=data.filename
    )
