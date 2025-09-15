"""
Utility modules for the web scraping application.
"""

from .logger import logger
from .signal_handler import (
    setup_graceful_shutdown,
    add_cleanup_callback,
    is_shutdown_requested,
)

__all__ = [
    "logger",
    "setup_graceful_shutdown",
    "add_cleanup_callback",
    "is_shutdown_requested",
]
