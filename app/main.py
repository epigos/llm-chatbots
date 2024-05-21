import logging
import sys
import typing
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db, logging_config
from app.config import settings
from app.routers import include_routers

logging_config.configure()


@asynccontextmanager
async def lifespan(_: FastAPI) -> typing.AsyncIterator[None]:
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    db.async_db.init(settings)
    yield
    await db.async_db.close()


app = FastAPI(
    debug=settings.debug, lifespan=lifespan, title=settings.app_name, docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
include_routers(app)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if settings.log_level == "DEBUG" else logging.INFO,
)
