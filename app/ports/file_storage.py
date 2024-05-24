import abc
import typing


class FileStorage(abc.ABC):
    """
    Abstract class for file storage.
    """

    @abc.abstractmethod
    def upload(self, file_name: str, fileobj: typing.IO[bytes]) -> str:
        """
        Uploads a file to the file storage
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def download(self, file_name: str) -> bytes:
        """
        Downloads a file from the storage
        """
        raise NotImplementedError()
