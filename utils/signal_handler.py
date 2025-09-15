"""
Signal handling utilities for graceful container shutdown.
Handles SIGTERM, SIGINT, and other signals to ensure clean application exit.
"""

import signal
import sys
import threading
from typing import Callable, Optional
from utils.logger import logger


class GracefulShutdownHandler:
    """Handles graceful shutdown of the application."""

    def __init__(self):
        self.shutdown_event = threading.Event()
        self.cleanup_callbacks = []
        self.is_shutting_down = False

    def add_cleanup_callback(self, callback: Callable[[], None]) -> None:
        """Add a cleanup callback to be executed during shutdown."""
        self.cleanup_callbacks.append(callback)

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logger.info(
            f"Received signal {signal_name} ({signum}), initiating graceful shutdown..."
        )

        if self.is_shutting_down:
            logger.warning("Already shutting down, ignoring additional signals")
            return

        self.is_shutting_down = True
        self.shutdown_event.set()

        # Execute cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                logger.debug(f"Executing cleanup callback: {callback.__name__}")
                callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback {callback.__name__}: {e}")

        logger.info("Graceful shutdown completed")
        sys.exit(0)

    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        # Handle SIGTERM (sent by Docker/Kubernetes for graceful shutdown)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Handle SIGHUP (reload signal)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, self.signal_handler)

        logger.info("Signal handlers configured for graceful shutdown")

    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        return self.shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """Wait for shutdown signal."""
        return self.shutdown_event.wait(timeout)


# Global instance for easy access
shutdown_handler = GracefulShutdownHandler()


def setup_graceful_shutdown() -> GracefulShutdownHandler:
    """Set up graceful shutdown handling."""
    shutdown_handler.setup_signal_handlers()
    return shutdown_handler


def add_cleanup_callback(callback: Callable[[], None]) -> None:
    """Add a cleanup callback (convenience function)."""
    shutdown_handler.add_cleanup_callback(callback)


def is_shutdown_requested() -> bool:
    """Check if shutdown has been requested (convenience function)."""
    return shutdown_handler.is_shutdown_requested()
