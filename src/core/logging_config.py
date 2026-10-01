import logging
import sys
from pathlib import Path

from loguru import logger


def _prepare_log_file_path(project_root: Path, folder_name: str, log_file_name: str) -> Path:
    """Creates the parent directory for a log file relative to the project root."""
    path = Path(folder_name) / log_file_name

    if not path.is_absolute():
        path = project_root / path

    absolute_path = path.resolve()
    absolute_path.parent.mkdir(parents=True, exist_ok=True)

    return absolute_path


def _configure_console_output(log_level: str) -> None:
    """Configures asynchronous log output to the console."""
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level,
        enqueue=True,
        backtrace=True,
        diagnose=False,
        colorize=True
    )


def _configure_file_output(log_file_path: str | Path, log_level: str) -> None:
    """Configures asynchronous error logging to a file."""
    file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    logger.add(
        str(log_file_path),
        format=file_format,
        level=log_level,
        rotation="5 MB",
        retention="3 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False
    )


def _mute_fastapi_logs():
    """Sets the log level to `WARNING` for uvicorn and FastAPI loggers."""
    loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi"
    ]
    for logger_name in loggers:
        standard_logger = logging.getLogger(logger_name)
        standard_logger.setLevel(logging.WARNING)


def init_logging(
    project_root: Path,
    folder_name: str = "logs",
    log_file_name: str = "app.log",
    log_level: str = "INFO"
) -> None:
    """Initializes non-blocking application logging with console and file handlers."""
    logger.remove()

    log_file_path = _prepare_log_file_path(
        project_root=project_root,
        folder_name=folder_name,
        log_file_name=log_file_name
    )

    _mute_fastapi_logs()
    _configure_console_output(log_level=log_level)
    _configure_file_output(log_file_path=log_file_path, log_level=log_level)

    logger.info("Logging successfully initialized")


def shutdown_logging() -> None:
    """Guarantees that all buffers from the queues are flushed to disk."""
    logger.complete()
    logger.info("Logging completed successfully")
