"""
Tests for the health check functionality.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest


def test_healthcheck_script_exists():
    """Test that the health check script exists."""
    healthcheck_path = Path("healthcheck.py")
    assert healthcheck_path.exists(), "healthcheck.py should exist"


def test_healthcheck_runs():
    """Test that the health check script runs without errors."""
    try:
        result = subprocess.run(
            [sys.executable, "healthcheck.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Health check should return valid JSON
        output = json.loads(result.stdout)

        # Check required fields
        assert "status" in output
        assert "timestamp" in output
        assert "checks" in output
        assert "overall" in output

        # Status should be either healthy or unhealthy
        assert output["status"] in ["healthy", "unhealthy", "error"]

        # Overall should be boolean
        assert isinstance(output["overall"], bool)

    except subprocess.TimeoutExpired:
        pytest.fail("Health check timed out")
    except json.JSONDecodeError:
        pytest.fail("Health check did not return valid JSON")
    except Exception as e:
        pytest.fail(f"Health check failed with error: {e}")


def test_healthcheck_checks_structure():
    """Test that health check returns expected check structure."""
    try:
        result = subprocess.run(
            [sys.executable, "healthcheck.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = json.loads(result.stdout)
        checks = output.get("checks", {})

        # Expected checks
        expected_checks = [
            "output_directory",
            "logs_directory",
            "dependencies",
            "target_website",
            "recent_activity",
        ]

        for check in expected_checks:
            assert check in checks, f"Health check should include '{check}'"
            assert isinstance(checks[check], bool), f"Check '{check}' should be boolean"

    except Exception as e:
        pytest.fail(f"Health check structure test failed: {e}")


def test_signal_handler_import():
    """Test that signal handler can be imported."""
    try:
        from utils.signal_handler import setup_graceful_shutdown, is_shutdown_requested

        assert callable(setup_graceful_shutdown)
        assert callable(is_shutdown_requested)
    except ImportError as e:
        pytest.fail(f"Failed to import signal handler: {e}")


def test_logger_container_mode():
    """Test that logger works in container mode."""
    import os

    # Set container environment
    original_env = os.environ.get("CONTAINER_ENV")
    os.environ["CONTAINER_ENV"] = "true"

    try:
        # Import logger (this will configure it)
        from utils.logger import logger

        # Test that we can log without errors
        logger.info("Test log message")

    finally:
        # Restore original environment
        if original_env is None:
            os.environ.pop("CONTAINER_ENV", None)
        else:
            os.environ["CONTAINER_ENV"] = original_env
