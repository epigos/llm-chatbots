import logging
import logging.config
import typing

import structlog

from app.config import settings

shared_processors: tuple[structlog.types.Processor, ...] = (
    structlog.contextvars.merge_contextvars,
    # # Add the name of the logger to event dict
    structlog.stdlib.add_logger_name,
    # # Add log level to event dict
    structlog.stdlib.add_log_level,
    # If the "exc_info" key in the event dict is either true or a
    # sys.exc_info() tuple, remove "exc_info" and render the exception
    # with traceback into the "exception" key.
    structlog.processors.format_exc_info,
    # Add a timestamp in ISO 8601 format
    structlog.processors.TimeStamper(fmt="iso"),
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    structlog.stdlib.ExtraAdder(),
)


class ExcludeAccessFilter(logging.Filter):
    """
    Filter access request logs
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Returns false for access request logs
        """
        return False


def get_logging_config() -> typing.Dict[str, typing.Any]:
    """
    Get logging configuration for the project
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"exclude_access_filter": {"()": ExcludeAccessFilter}},
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": shared_processors,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
                "foreign_pre_chain": shared_processors,
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": shared_processors,
            },
        },
        "handlers": {
            "default": {
                "level": settings.log_level,
                "class": "logging.StreamHandler",
                "formatter": settings.log_format,
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": settings.log_level},
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "faker.factory": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "factory.generate": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
                "filters": ["exclude_access_filter"],
            },
            "sqlalchemy.engine.Engine": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "httpcore.http11": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def configure() -> None:
    """Configure the logging format for the project"""
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
