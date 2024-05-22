import logging
from unittest import mock

import fastapi
import pytest
from starlette import routing

from app import middlewares


@pytest.mark.parametrize(
    ["content_type", "content"],
    [
        ("application/json", '{"a": "b"}'),
        ("plain/text", "plain response"),
    ],
)
@pytest.mark.asyncio
async def test_catch_exceptions_middleware_ok(
    content_type, content, caplog: pytest.LogCaptureFixture
):
    request = fastapi.Request(
        scope=dict(
            type="http",
            method="GET",
            path="/test",
            headers={},
            route=routing.Route(path="/test", endpoint=mock.Mock()),
            root_path="",
        )
    )
    call_next_mock = mock.AsyncMock()
    call_next_mock.return_value = fastapi.Response(
        content=content, media_type=content_type
    )
    with caplog.at_level(logging.INFO):
        await middlewares.catch_exceptions_middleware(
            request=request, call_next=call_next_mock
        )
        expected_headers = {
            "content-length": "10",
            "content-type": "application/json",
        }
        if content_type == "plain/text":
            expected_headers = {
                "content-length": "14",
                "content-type": "plain/text",
            }
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "api response"
        assert caplog.records[0].requestPath == "/test"
        assert isinstance(caplog.records[0].requestLatency, str)
        assert caplog.records[0].status_code == 200
        assert caplog.records[0].headers == expected_headers


@pytest.mark.asyncio
async def test_catch_exceptions_middleware_exceptions(caplog: pytest.LogCaptureFixture):
    request = fastapi.Request(
        scope=dict(
            type="http",
            method="GET",
            path="/test",
            headers={},
            route=routing.Route(path="/test", endpoint=mock.Mock()),
            root_path="",
            app=mock.AsyncMock(spec_set=fastapi.FastAPI),
        )
    )
    call_next_mock = mock.AsyncMock(side_effect=RuntimeError("test"))

    with caplog.at_level(logging.DEBUG):
        await middlewares.catch_exceptions_middleware(
            request=request, call_next=call_next_mock
        )

        assert len(caplog.records) == 2
        assert caplog.records[0].levelname == "ERROR"

        assert caplog.records[1].levelname == "INFO"
        assert caplog.records[1].message == "api response"
        assert caplog.records[1].requestPath == "/test"
        assert isinstance(caplog.records[1].requestLatency, str)
        assert caplog.records[1].status_code == 500
