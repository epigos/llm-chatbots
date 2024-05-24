import io

from app.adapters import aws


def test_can_upload_and_download_file(s3_bucket: str) -> None:
    test_file = b"test"
    storage = aws.FileStorage(s3_bucket)

    with io.BytesIO(test_file) as buffer:
        loc = storage.upload("test.txt", buffer)

    assert loc == "test.txt"
    downloaded_file = storage.download(loc)
    assert downloaded_file == test_file
