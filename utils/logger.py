import os
from pathlib import Path
from loguru import logger

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logger
logger.add(
    logs_dir / "app.log",
    rotation="10 MB",  # Rotate when file reaches 10MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated files
    level="INFO",  # Default log level
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True,  # Thread-safe logging
    backtrace=True,  # Enable exception traceback
    diagnose=True,  # Show variable values in traceback
)

# Export logger for use in other modules
__all__ = ["logger"]
