from __future__ import annotations

import datetime
import time
import typing

import boto3
from mypy_boto3_s3.client import S3Client

from app.config import settings


def utcnow() -> datetime.datetime:
    """Generates timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


class AsyncElapsedTimer:
    """
    Measures elapsed time in milliseconds
    """

    def __init__(self) -> None:
        self._start = 0.0
        self._end = 0.0
        self.elapsed = 0.0
        self.elapsed_formatted = "0 ms"

    async def __aenter__(self) -> AsyncElapsedTimer:
        self._start = time.perf_counter()  # Use perf_counter for high-resolution timer
        return self

    async def __aexit__(self, *args: tuple[typing.Any]) -> None:
        self._end = time.perf_counter()
        self.elapsed = (self._end - self._start) * 1000  # Convert to milliseconds
        self.elapsed_formatted = f"{self.elapsed:.0f} ms"  # Format as integer


def get_s3_client() -> S3Client:
    """
    Returns boto3 s3 client
    """
    client = boto3.client(
        "s3",
        region_name=settings.aws_default_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
    )
    return typing.cast(S3Client, client)
