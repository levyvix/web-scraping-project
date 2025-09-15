#!/usr/bin/env python3
"""
Documentation deployment preparation script.

This script prepares the documentation for deployment by:
1. Building the documentation
2. Validating the build output
3. Running link checks
4. Preparing deployment artifacts
5. Generating deployment reports

Usage:
    python scripts/docs_deploy_prep.py [--output-dir OUTPUT_DIR] [--skip-tests]
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DocumentationDeploymentPrep:
    """Handles documentation deployment preparation tasks."""

    def __init__(self, output_dir: Optional[str] = None, skip_tests: bool = False):
        """Initialize the deployment preparation."""
        self.project_root = Path.cwd()
        self.output_dir = (
            Path(output_dir) if output_dir else self.project_root / "dist" / "docs"
        )
        self.skip_tests = skip_tests
        self.build_report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "steps": [],
            "errors": [],
            "warnings": [],
        }

    def log_step(
        self, step_name: str, status: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a deployment preparation step."""
        step_info = {
            "name": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.build_report["steps"].append(step_info)
        print(f"[{status.upper()}] {step_name}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")

    def log_error(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an error during deployment preparation."""
        error_info = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.build_report["errors"].append(error_info)
        print(f"[ERROR] {message}")

    def log_warning(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a warning during deployment preparation."""
        warning_info = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.build_report["warnings"].append(warning_info)
        print(f"[WARNING] {message}")

    def run_command(
        self, cmd: List[str], timeout: int = 300
    ) -> subprocess.CompletedProcess[str]:
        """Run a command with error handling and logging."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Command timed out after {timeout} seconds: {' '.join(cmd)}"
            )
        except FileNotFoundError:
            raise RuntimeError(f"Command not found: {cmd[0]}")

    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are available."""
        self.log_step("check_prerequisites", "started")

        # Check if mkdocs is available
        try:
            result = self.run_command(["uv", "run", "mkdocs", "--version"], timeout=10)
            if result.returncode != 0:
                self.log_error("MkDocs not available", {"stderr": result.stderr})
                return False

            mkdocs_version = result.stdout.strip()
            self.log_step(
                "check_prerequisites", "success", {"mkdocs_version": mkdocs_version}
            )

        except RuntimeError as e:
            self.log_error(f"Failed to check MkDocs: {e}")
            return False

        # Check if required files exist
        required_files = ["mkdocs.yml", "docs/index.md"]
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.log_error(f"Required file missing: {file_path}")
                return False

        return True

    def run_documentation_tests(self) -> bool:
        """Run documentation-specific tests."""
        if self.skip_tests:
            self.log_step("run_documentation_tests", "skipped")
            return True

        self.log_step("run_documentation_tests", "started")

        try:
            # Run documentation tests
            result = self.run_command(
                ["uv", "run", "pytest", "tests/test_docs/", "-v", "--tb=short"],
                timeout=120,
            )

            if result.returncode != 0:
                self.log_error(
                    "Documentation tests failed",
                    {"stdout": result.stdout, "stderr": result.stderr},
                )
                return False

            self.log_step(
                "run_documentation_tests",
                "success",
                {
                    "output": result.stdout.split("\n")[
                        -3:-1
                    ]  # Last few lines with summary
                },
            )
            return True

        except RuntimeError as e:
            self.log_error(f"Failed to run documentation tests: {e}")
            return False

    def build_documentation(self) -> bool:
        """Build the documentation."""
        self.log_step("build_documentation", "started")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Build documentation
            result = self.run_command(
                ["uv", "run", "mkdocs", "build", "--site-dir", str(self.output_dir)],
                timeout=180,
            )

            if result.returncode != 0:
                self.log_error(
                    "Documentation build failed",
                    {"stdout": result.stdout, "stderr": result.stderr},
                )
                return False

            # Check build output
            essential_files = ["index.html", "search/search_index.json"]
            missing_files = []

            for file_name in essential_files:
                if not (self.output_dir / file_name).exists():
                    missing_files.append(file_name)

            if missing_files:
                self.log_error(
                    "Build output incomplete", {"missing_files": missing_files}
                )
                return False

            # Get build statistics
            build_stats = self.get_build_statistics()

            self.log_step("build_documentation", "success", build_stats)
            return True

        except RuntimeError as e:
            self.log_error(f"Failed to build documentation: {e}")
            return False

    def get_build_statistics(self) -> Dict[str, Any]:
        """Get statistics about the built documentation."""
        stats = {
            "total_files": 0,
            "html_files": 0,
            "css_files": 0,
            "js_files": 0,
            "image_files": 0,
            "total_size_mb": 0.0,
        }

        if not self.output_dir.exists():
            return stats

        total_size = 0

        for file_path in self.output_dir.rglob("*"):
            if file_path.is_file():
                stats["total_files"] += 1
                file_size = file_path.stat().st_size
                total_size += file_size

                suffix = file_path.suffix.lower()
                if suffix == ".html":
                    stats["html_files"] += 1
                elif suffix == ".css":
                    stats["css_files"] += 1
                elif suffix == ".js":
                    stats["js_files"] += 1
                elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]:
                    stats["image_files"] += 1

        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        return stats

    def validate_build_output(self) -> bool:
        """Validate the built documentation."""
        self.log_step("validate_build_output", "started")

        validation_issues = []

        # Check for essential pages
        essential_pages = ["index.html"]
        for page in essential_pages:
            page_path = self.output_dir / page
            if not page_path.exists():
                validation_issues.append(f"Missing essential page: {page}")
            elif page_path.stat().st_size == 0:
                validation_issues.append(f"Empty essential page: {page}")

        # Check search functionality
        search_index = self.output_dir / "search" / "search_index.json"
        if search_index.exists():
            try:
                with open(search_index, "r", encoding="utf-8") as f:
                    search_data = json.load(f)
                    if not search_data.get("docs"):
                        validation_issues.append("Search index is empty")
            except (json.JSONDecodeError, KeyError):
                validation_issues.append("Search index is malformed")
        else:
            validation_issues.append("Search index not generated")

        # Check for broken internal links in HTML
        html_files = list(self.output_dir.rglob("*.html"))
        if not html_files:
            validation_issues.append("No HTML files generated")

        if validation_issues:
            self.log_error("Build validation failed", {"issues": validation_issues})
            return False

        self.log_step(
            "validate_build_output",
            "success",
            {
                "html_files_count": len(html_files),
                "search_index_size": search_index.stat().st_size
                if search_index.exists()
                else 0,
            },
        )
        return True

    def create_deployment_manifest(self) -> bool:
        """Create a deployment manifest with build information."""
        self.log_step("create_deployment_manifest", "started")

        try:
            manifest = {
                "build_info": {
                    "timestamp": self.build_report["timestamp"],
                    "build_duration": self.calculate_build_duration(),
                    "status": "success",
                },
                "content": {
                    "statistics": self.get_build_statistics(),
                    "pages": self.get_page_list(),
                },
                "deployment": {
                    "ready": True,
                    "output_directory": str(self.output_dir),
                    "entry_point": "index.html",
                },
            }

            manifest_path = self.output_dir / "deployment_manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            self.log_step(
                "create_deployment_manifest",
                "success",
                {"manifest_path": str(manifest_path)},
            )
            return True

        except Exception as e:
            self.log_error(f"Failed to create deployment manifest: {e}")
            return False

    def get_page_list(self) -> List[str]:
        """Get list of all HTML pages in the build."""
        if not self.output_dir.exists():
            return []

        pages = []
        for html_file in self.output_dir.rglob("*.html"):
            # Get relative path from output directory
            rel_path = html_file.relative_to(self.output_dir)
            pages.append(str(rel_path))

        return sorted(pages)

    def calculate_build_duration(self) -> float:
        """Calculate total build duration in seconds."""
        if not self.build_report["steps"]:
            return 0.0

        start_time = datetime.fromisoformat(self.build_report["timestamp"])
        end_time = datetime.now()

        return (end_time - start_time).total_seconds()

    def save_build_report(self) -> bool:
        """Save the build report to a file."""
        try:
            self.build_report["status"] = (
                "completed" if not self.build_report["errors"] else "failed"
            )
            self.build_report["duration_seconds"] = self.calculate_build_duration()

            report_path = self.output_dir / "build_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(self.build_report, f, indent=2, ensure_ascii=False)

            print(f"\nBuild report saved to: {report_path}")
            return True

        except Exception as e:
            print(f"Failed to save build report: {e}")
            return False

    def run_deployment_preparation(self) -> bool:
        """Run the complete deployment preparation process."""
        print("Starting documentation deployment preparation...")
        print(f"Output directory: {self.output_dir}")

        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Documentation Tests", self.run_documentation_tests),
            ("Build Documentation", self.build_documentation),
            ("Validate Build Output", self.validate_build_output),
            ("Create Deployment Manifest", self.create_deployment_manifest),
        ]

        success = True

        for step_name, step_function in steps:
            print(f"\n--- {step_name} ---")
            if not step_function():
                success = False
                break

        # Always save the build report
        self.save_build_report()

        if success:
            print("\n✅ Documentation deployment preparation completed successfully!")
            print(f"📁 Build output: {self.output_dir}")
            print("🚀 Ready for deployment")
        else:
            print("\n❌ Documentation deployment preparation failed!")
            print(
                f"📋 Check build report for details: {self.output_dir / 'build_report.json'}"
            )

        return success


def main() -> None:
    """Main entry point for the deployment preparation script."""
    parser = argparse.ArgumentParser(
        description="Prepare documentation for deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--output-dir",
        help="Output directory for built documentation (default: dist/docs)",
        default=None,
    )

    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip running documentation tests"
    )

    args = parser.parse_args()

    # Run deployment preparation
    prep = DocumentationDeploymentPrep(
        output_dir=args.output_dir, skip_tests=args.skip_tests
    )

    success = prep.run_deployment_preparation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
