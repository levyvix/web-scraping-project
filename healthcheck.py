#!/usr/bin/env python3
"""
Health check script for the web scraper container.
This script verifies that the application is healthy and ready to process requests.
"""

import sys
import json
import importlib.util
from datetime import datetime, timedelta
import requests
from typing import Dict, Any
from paths import output_directory, logs_directory


def check_output_directory() -> bool:
    """Check if output directory is writable."""
    try:
        output_dir = output_directory()
        output_dir.mkdir(exist_ok=True)
        test_file = output_dir / ".health_check"
        test_file.write_text("health_check")
        test_file.unlink()
        return True
    except Exception:
        return False


def check_logs_directory() -> bool:
    """Check if logs directory is writable."""
    try:
        logs_dir = logs_directory()
        logs_dir.mkdir(exist_ok=True)
        test_file = logs_dir / ".health_check"
        test_file.write_text("health_check")
        test_file.unlink()
        return True
    except Exception:
        return False


def check_dependencies() -> bool:
    """Check if critical dependencies are available."""
    required_modules = ["scrapling", "loguru", "tqdm", "concurrent.futures"]

    for module_name in required_modules:
        if importlib.util.find_spec(module_name) is None:
            return False

    return True


def check_target_website() -> bool:
    """Check if the target website is accessible."""
    try:
        response = requests.get("https://books.toscrape.com/", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def check_recent_activity() -> bool:
    """Check if there's been recent scraping activity (optional check)."""
    try:
        output_file = output_directory() / "books.json"
        if not output_file.exists():
            return True  # No output yet is okay

        file_mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        return file_mtime > twenty_four_hours_ago
    except Exception:
        return True  # If we can't check, assume it's okay


def run_health_check() -> Dict[str, Any]:
    """Run all health checks and return results."""
    checks = {
        "output_directory": check_output_directory(),
        "logs_directory": check_logs_directory(),
        "dependencies": check_dependencies(),
        "target_website": check_target_website(),
        "recent_activity": check_recent_activity(),
    }

    all_passed = all(checks.values())

    return {
        "status": "healthy" if all_passed else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "overall": all_passed,
    }


def main() -> int:
    """Main health check function."""
    try:
        result = run_health_check()

        print(json.dumps(result, indent=2))

        return 0 if result["overall"] else 1

    except Exception as e:
        error_result = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "overall": False,
        }
        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
