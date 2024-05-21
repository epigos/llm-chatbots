from __future__ import annotations

import datetime
import time
import typing


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
