"""
Tests for the health check functionality.
"""

import json
import healthcheck


def test_healthcheck_reports_probe_results(monkeypatch):
    probes = {
        "check_output_directory": True,
        "check_logs_directory": True,
        "check_dependencies": True,
        "check_target_website": False,
        "check_recent_activity": True,
    }
    for probe, result in probes.items():
        monkeypatch.setattr(healthcheck, probe, lambda result=result: result)

    result = healthcheck.run_health_check()

    assert result["status"] == "unhealthy"
    assert result["checks"] == {
        "output_directory": True,
        "logs_directory": True,
        "dependencies": True,
        "target_website": False,
        "recent_activity": True,
    }
    assert result["overall"] is False


def test_healthcheck_cli_serializes_status(monkeypatch, capsys):
    monkeypatch.setattr(
        healthcheck,
        "run_health_check",
        lambda: {
            "status": "healthy",
            "timestamp": "now",
            "checks": {},
            "overall": True,
        },
    )

    assert healthcheck.main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "healthy"
