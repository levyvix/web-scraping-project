#!/usr/bin/env python3
"""
Health check script for the web scraper container.
This script verifies that the application is healthy and ready to process requests.
"""

import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
import requests
from typing import Dict, Any


def check_output_directory() -> bool:
    """Check if output directory is writable."""
    try:
        # Check container path first, then local path
        if Path("/app/output").exists():
            output_dir = Path("/app/output")
        else:
            output_dir = Path("./output")

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
        # Check container path first, then local path
        if Path("/app/logs").exists():
            logs_dir = Path("/app/logs")
        else:
            logs_dir = Path("./logs")

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
        # Check container path first, then local path
        if Path("/app/output/books.json").exists():
            output_file = Path("/app/output/books.json")
        elif Path("./output/books.json").exists():
            output_file = Path("./output/books.json")
        else:
            return True  # No output yet is okay

        # Check if file was modified in the last 24 hours (indicates recent activity)
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

        # Print result as JSON for container orchestration tools
        print(json.dumps(result, indent=2))

        # Return appropriate exit code
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
