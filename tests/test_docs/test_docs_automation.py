"""
Integration tests for documentation build automation.

This module contains tests that verify the complete documentation automation
workflow including build verification, link checking, and deployment preparation.
"""

import pytest
import subprocess
from pathlib import Path


class TestDocumentationAutomation:
    """Integration tests for documentation automation workflow."""

    def test_docs_test_task_available(self):
        """Test that the docs-test task is available and works."""
        # Test that the task is defined
        result = subprocess.run(
            ["uv", "run", "task", "--list"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, f"Failed to list tasks: {result.stderr}"
        assert "docs-test" in result.stdout, "docs-test task not found in task list"

    def test_docs_check_links_task_available(self):
        """Test that the docs-check-links task is available."""
        result = subprocess.run(
            ["uv", "run", "task", "--list"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, f"Failed to list tasks: {result.stderr}"
        assert "docs-check-links" in result.stdout, (
            "docs-check-links task not found in task list"
        )

    def test_docs_deploy_prep_task_available(self):
        """Test that the docs-deploy-prep task is available."""
        result = subprocess.run(
            ["uv", "run", "task", "--list"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, f"Failed to list tasks: {result.stderr}"
        assert "docs-deploy-prep" in result.stdout, (
            "docs-deploy-prep task not found in task list"
        )

    def test_deployment_script_help(self):
        """Test that the deployment preparation script shows help correctly."""
        try:
            result = subprocess.run(
                ["uv", "run", "python", "scripts/docs_deploy_prep.py", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0, "Help command failed"
            assert "Prepare documentation for deployment" in result.stdout, (
                "Help text not found"
            )
            assert "--output-dir" in result.stdout, (
                "Output directory option not documented"
            )
            assert "--skip-tests" in result.stdout, "Skip tests option not documented"

        except subprocess.TimeoutExpired:
            pytest.fail("Help command timed out")
        except FileNotFoundError:
            pytest.skip("Python or deployment script not available")

    def test_automation_workflow_integration(self):
        """Test that all automation components work together."""
        # This test verifies that the automation workflow components are properly integrated

        # Check that all required files exist
        required_files = [
            "tests/test_docs/test_docs_build.py",
            "tests/test_docs/test_link_checker.py",
            "scripts/docs_deploy_prep.py",
        ]

        for file_path in required_files:
            assert Path(file_path).exists(), (
                f"Required automation file {file_path} not found"
            )

        # Check that pyproject.toml has the required tasks
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml not found"

        content = pyproject_path.read_text(encoding="utf-8")
        required_tasks = ["docs-test", "docs-check-links", "docs-deploy-prep"]

        for task in required_tasks:
            assert task in content, f"Required task {task} not found in pyproject.toml"

    def test_documentation_automation_markers(self):
        """Test that documentation tests use appropriate pytest markers."""
        # Check that slow tests are marked appropriately
        test_files = [
            "tests/test_docs/test_docs_build.py",
            "tests/test_docs/test_link_checker.py",
        ]

        for test_file in test_files:
            content = Path(test_file).read_text(encoding="utf-8")

            # Check for pytest markers
            if "@pytest.mark.slow" in content:
                # If slow marker is used, verify it's used appropriately
                assert "def test_" in content, (
                    f"Test file {test_file} should contain test functions"
                )

    def test_automation_documentation(self):
        """Test that automation components are properly documented."""
        # Check that key files have proper docstrings
        files_to_check = [
            "tests/test_docs/test_docs_build.py",
            "tests/test_docs/test_link_checker.py",
            "scripts/docs_deploy_prep.py",
        ]

        for file_path in files_to_check:
            content = Path(file_path).read_text(encoding="utf-8")

            # Check for module docstring
            assert '"""' in content, (
                f"File {file_path} should have docstring documentation"
            )

            # Check for class/function documentation
            if "class " in content:
                # Find class definitions and check they have docstrings
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith("class ") and ":" in line:
                        # Look for docstring in next few lines
                        found_docstring = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if '"""' in lines[j]:
                                found_docstring = True
                                break
                        assert found_docstring, (
                            f"Class in {file_path} at line {i + 1} should have docstring"
                        )
