import io
import typing

from app import ports
from app.utils import get_s3_client


class FileStorage(ports.FileStorage):
    """
    Implementation of the FileStorage interface for AWS S3.
    """

    def __init__(self, bucket_name: str):
        self._bucket_name = bucket_name
        self._s3_client = get_s3_client()

    def upload(self, file_name: str, fileobj: typing.IO[bytes]) -> str:
        self._s3_client.upload_fileobj(
            Bucket=self._bucket_name, Key=file_name, Fileobj=fileobj
        )
        return file_name

    def download(self, file_name: str) -> bytes:
        with io.BytesIO() as buffer:
            self._s3_client.download_fileobj(
                Bucket=self._bucket_name, Key=file_name, Fileobj=buffer
            )
            return buffer.getvalue()
