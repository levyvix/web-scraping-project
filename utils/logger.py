from loguru import logger
import os
import sys
import json
from paths import logs_directory, uses_container_paths

logs_dir = logs_directory()
logs_dir.mkdir(exist_ok=True)

IS_CONTAINER = (
    os.getenv("CONTAINER_ENV", "false").lower() == "true" or uses_container_paths()
)


def json_formatter(record):
    """Format log records as JSON for container environments."""
    serialized = json.dumps(
        {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "module": record["module"],
            "process": record["process"].id if record["process"] else None,
            "thread": record["thread"].id if record["thread"] else None,
        }
    )
    return serialized.replace("{", "{{").replace("}", "}}") + "\n"


logger.remove()

if IS_CONTAINER:
    logger.add(
        sys.stdout,
        format=json_formatter,
        level=os.getenv("LOG_LEVEL", "INFO"),
        enqueue=True,
        backtrace=True,
        diagnose=False,  # Disable in production for security
    )
else:
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=os.getenv("LOG_LEVEL", "INFO"),
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

logger.add(
    logs_dir / "app.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

__all__ = ["logger"]
