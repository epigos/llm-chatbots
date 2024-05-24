import json
from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient

from app import models
from app.routers.uploads.schemas import ACCEPTED_EXTENSIONS

pytestmark = pytest.mark.asyncio

path = "/uploads/"


async def test_uploads_validation_errors(client: AsyncClient, s3_bucket) -> None:
    response = await client.post(path, data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text

    data = json.loads(response.text)
    assert data["detail"][0]["loc"] == ["body", "file"]
    assert data["detail"][0]["msg"] == "Field required"

    assert data["detail"][1]["loc"] == ["body", "bot_id"]
    assert data["detail"][1]["msg"] == "Field required"


@pytest.mark.parametrize("filename", ["example.jpeg", "example.png", "example.exe"])
async def test_upload_invalid_file_extension(
    client: AsyncClient, bot_db: models.Bot, s3_bucket: str, filename: str
) -> None:
    file_content = b"test content"
    files = {"file": (filename, file_content, "application/octet-stream")}

    response = await client.post(path, files=files, data={"bot_id": str(bot_db.id)})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = json.loads(response.text)
    assert data["detail"][0]["loc"] == ["filename"]

    ext = Path(filename).suffix
    expected_msg = f"Invalid file extension: {ext}. Accepted extensions are: {', '.join(ACCEPTED_EXTENSIONS)}"
    assert expected_msg in data["detail"][0]["msg"]


@pytest.mark.parametrize(
    "filename,content_type",
    [
        ("example.txt", "plain/text"),
        ("example.doc", "application/doc"),
        ("example.docx", "application/doc"),
        ("example.pdf", "application/pdf"),
    ],
)
async def test_can_upload_files(
    client: AsyncClient,
    bot_db: models.Bot,
    s3_bucket: str,
    filename: str,
    content_type: str,
) -> None:
    file_content = b"test content"
    files = {"file": (filename, file_content, content_type)}

    response = await client.post(
        path,
        files=files,
        data={"bot_id": str(bot_db.id)},
        headers={"accept": "application/json"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert str(bot_db.id) in data["location"]
    assert data["filename"] == filename
    assert data["content_type"] == content_type
