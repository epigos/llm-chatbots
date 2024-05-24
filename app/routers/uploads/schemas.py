from pathlib import Path

from pydantic import field_validator

from app.routers import common_schemas as common

ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"]


class UploadFileInput(common.BaseInputSchema):
    """
    Schema for file upload
    """

    filename: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """
        validates filename against accepted extensions
        """
        ext = Path(v).suffix
        if ext not in ACCEPTED_EXTENSIONS:
            raise ValueError(
                f"Invalid file extension: {ext}. Accepted extensions are: {', '.join(ACCEPTED_EXTENSIONS)}"
            )
        return v

    @property
    def extension(self) -> str:
        """
        Returns file extension
        """
        return Path(self.filename).suffix


class FileUploadOutput(common.BaseOutputSchema):
    """
    Schema for file upload response
    """

    location: str
    filename: str
    content_type: str | None = None
