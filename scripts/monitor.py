#!/usr/bin/env python3
"""
Container monitoring script for the web scraper.
Provides monitoring capabilities for container orchestration and operations teams.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def get_container_status(container_name: str = "book-scraper") -> Dict[str, Any]:
    """Get the status of the scraper container."""
    try:
        # Get container info
        result = subprocess.run(
            ["docker", "inspect", container_name],
            capture_output=True,
            text=True,
            check=True,
        )

        container_info = json.loads(result.stdout)[0]
        state = container_info["State"]

        return {
            "container_name": container_name,
            "status": state.get("Status", "unknown"),
            "running": state.get("Running", False),
            "started_at": state.get("StartedAt"),
            "finished_at": state.get("FinishedAt"),
            "exit_code": state.get("ExitCode"),
            "health": state.get("Health", {}).get("Status", "none"),
            "restart_count": container_info.get("RestartCount", 0),
        }
    except subprocess.CalledProcessError:
        return {
            "container_name": container_name,
            "status": "not_found",
            "running": False,
            "error": "Container not found or Docker not available",
        }
    except Exception as e:
        return {
            "container_name": container_name,
            "status": "error",
            "running": False,
            "error": str(e),
        }


def get_container_logs(
    container_name: str = "book-scraper", lines: int = 50
) -> Dict[str, Any]:
    """Get recent logs from the container."""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            check=True,
        )

        return {
            "logs": result.stdout.split("\n"),
            "errors": result.stderr.split("\n") if result.stderr else [],
            "lines_retrieved": lines,
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get logs: {e}", "logs": [], "errors": []}


def get_health_check_status(container_name: str = "book-scraper") -> Dict[str, Any]:
    """Run health check and get detailed status."""
    try:
        # Run health check inside container
        result = subprocess.run(
            ["docker", "exec", container_name, "python", "healthcheck.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout:
            try:
                health_data = json.loads(result.stdout)
                return {
                    "health_check_available": True,
                    "health_data": health_data,
                    "exit_code": result.returncode,
                }
            except json.JSONDecodeError:
                return {
                    "health_check_available": True,
                    "health_data": {"raw_output": result.stdout},
                    "exit_code": result.returncode,
                }
        else:
            return {
                "health_check_available": False,
                "error": "No health check output",
                "exit_code": result.returncode,
            }

    except subprocess.TimeoutExpired:
        return {"health_check_available": False, "error": "Health check timed out"}
    except subprocess.CalledProcessError as e:
        return {"health_check_available": False, "error": f"Health check failed: {e}"}


def get_output_status() -> Dict[str, Any]:
    """Check the status of output files."""
    try:
        output_dir = Path("./output")
        logs_dir = Path("./logs")

        output_files = list(output_dir.glob("*.json")) if output_dir.exists() else []
        log_files = list(logs_dir.glob("*.log")) if logs_dir.exists() else []

        output_info = []
        for file in output_files:
            stat = file.stat()
            output_info.append(
                {
                    "name": file.name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        log_info = []
        for file in log_files:
            stat = file.stat()
            log_info.append(
                {
                    "name": file.name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return {
            "output_directory_exists": output_dir.exists(),
            "logs_directory_exists": logs_dir.exists(),
            "output_files": output_info,
            "log_files": log_info,
            "total_output_files": len(output_files),
            "total_log_files": len(log_files),
        }

    except Exception as e:
        return {
            "error": f"Failed to check output status: {e}",
            "output_files": [],
            "log_files": [],
        }


def monitor_container(
    container_name: str = "book-scraper", watch: bool = False, interval: int = 30
) -> None:
    """Monitor container status and health."""

    def get_full_status():
        return {
            "timestamp": datetime.now().isoformat(),
            "container": get_container_status(container_name),
            "health": get_health_check_status(container_name),
            "output": get_output_status(),
        }

    if watch:
        print(
            f"Monitoring container '{container_name}' every {interval} seconds. Press Ctrl+C to stop."
        )
        try:
            while True:
                status = get_full_status()
                print(f"\n--- {status['timestamp']} ---")
                print(f"Container Status: {status['container']['status']}")
                print(
                    f"Health Status: {status['health'].get('health_data', {}).get('status', 'unknown')}"
                )
                print(f"Output Files: {status['output']['total_output_files']}")
                print(f"Log Files: {status['output']['total_log_files']}")

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    else:
        status = get_full_status()
        print(json.dumps(status, indent=2))


def main():
    """Main monitoring function."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor web scraper container")
    parser.add_argument(
        "--container",
        default="book-scraper",
        help="Container name to monitor (default: book-scraper)",
    )
    parser.add_argument(
        "--watch", action="store_true", help="Continuously monitor the container"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitoring interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--logs", action="store_true", help="Show recent container logs"
    )
    parser.add_argument("--health", action="store_true", help="Run health check only")

    args = parser.parse_args()

    if args.logs:
        logs = get_container_logs(args.container)
        print(json.dumps(logs, indent=2))
    elif args.health:
        health = get_health_check_status(args.container)
        print(json.dumps(health, indent=2))
    else:
        monitor_container(args.container, args.watch, args.interval)


if __name__ == "__main__":
    main()
