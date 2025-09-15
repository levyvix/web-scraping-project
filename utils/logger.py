from pathlib import Path
from loguru import logger
import os
import sys
import json

# Create logs directory if it doesn't exist
# Use /app/logs in container environment, fallback to relative path for local development
if os.path.exists("/app/logs"):
    logs_dir = Path("/app/logs")
else:
    logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Check if running in container environment
IS_CONTAINER = os.getenv("CONTAINER_ENV", "false").lower() == "true" or os.path.exists(
    "/app/logs"
)


# Configure structured logging for containers
def json_formatter(record):
    """Format log records as JSON for container environments."""
    return (
        json.dumps(
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
        + "\n"
    )


# Remove default handler
logger.remove()

# Add console handler with appropriate format
if IS_CONTAINER:
    # Structured JSON logging for containers
    logger.add(
        sys.stdout,
        format=json_formatter,
        level=os.getenv("LOG_LEVEL", "INFO"),
        enqueue=True,
        backtrace=True,
        diagnose=False,  # Disable in production for security
    )
else:
    # Human-readable format for local development
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=os.getenv("LOG_LEVEL", "INFO"),
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

# Add file handler
logger.add(
    logs_dir / "app.log",
    rotation="10 MB",  # Rotate when file reaches 10MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated files
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True,  # Thread-safe logging
    backtrace=True,  # Enable exception traceback
    diagnose=True,  # Show variable values in traceback
)

# Export logger for use in other modules
__all__ = ["logger"]
