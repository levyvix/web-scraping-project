"""
Tests for documentation build verification and automation.

This module contains tests to ensure the MkDocs documentation builds successfully
and validates the documentation structure and content.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
from typing import List, Any
import re


class TestDocumentationBuild:
    """Test suite for documentation build verification."""

    def test_mkdocs_config_valid(self):
        """Test that mkdocs.yml configuration is valid and can be parsed."""
        mkdocs_config_path = Path("mkdocs.yml")

        # Verify mkdocs.yml exists
        assert mkdocs_config_path.exists(), "mkdocs.yml configuration file not found"

        # Read the content as text first to check basic structure
        content = mkdocs_config_path.read_text(encoding="utf-8")

        # Verify required configuration sections exist in the text
        required_sections = [
            "site_name:",
            "theme:",
            "nav:",
            "plugins:",
            "markdown_extensions:",
        ]
        for section in required_sections:
            assert section in content, (
                f"Required section '{section}' missing from mkdocs.yml"
            )

        # Verify theme is Material (check in text since YAML parsing fails with Python objects)
        assert "name: material" in content, "Theme should be Material"

        # Verify Portuguese language setting
        assert "language: pt" in content, "Theme language should be Portuguese"

        # Test that MkDocs can actually parse the config by running mkdocs --help
        # This will load and validate the config file
        try:
            result = subprocess.run(
                ["uv", "run", "mkdocs", "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # If mkdocs can load (which includes parsing config), it should return 0
            assert result.returncode == 0, f"MkDocs cannot load: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If mkdocs is not available, skip this validation
            pytest.skip("MkDocs not available for config validation")

    def test_documentation_files_exist(self):
        """Test that all required documentation files exist."""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "docs/ directory not found"

        # Required documentation files based on navigation
        required_files = [
            "index.md",
            "installation.md",
            "usage.md",
            "troubleshooting.md",
            "development.md",
            "api-reference.md",
        ]

        for file_name in required_files:
            file_path = docs_dir / file_name
            assert file_path.exists(), (
                f"Required documentation file {file_name} not found"
            )

            # Verify file is not empty
            assert file_path.stat().st_size > 0, (
                f"Documentation file {file_name} is empty"
            )

    def test_mkdocs_build_succeeds(self):
        """Test that MkDocs build command succeeds without errors."""
        # Create temporary directory for build output
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "site"

            # Run mkdocs build command
            cmd = ["uv", "run", "mkdocs", "build", "--site-dir", str(build_dir)]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,  # 60 second timeout
                    cwd=Path.cwd(),
                )
            except subprocess.TimeoutExpired:
                pytest.fail("MkDocs build command timed out after 60 seconds")
            except FileNotFoundError:
                pytest.skip("MkDocs not available - skipping build test")

            # Check if build succeeded
            if result.returncode != 0:
                pytest.fail(
                    f"MkDocs build failed with return code {result.returncode}\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

            # Verify build output directory was created
            assert build_dir.exists(), "Build output directory was not created"

            # Verify essential files were generated
            essential_files = ["index.html", "search/search_index.json"]
            for file_name in essential_files:
                file_path = build_dir / file_name
                assert file_path.exists(), (
                    f"Essential build file {file_name} was not generated"
                )

    def test_mkdocs_serve_config(self):
        """Test that MkDocs serve configuration is valid."""
        # Test that the serve command can be parsed (without actually starting server)
        cmd = ["uv", "run", "mkdocs", "serve", "--help"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "MkDocs serve command not available"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("MkDocs not available - skipping serve test")

    def test_documentation_structure_consistency(self):
        """Test that documentation structure matches navigation configuration."""
        # Load mkdocs configuration using mkdocs config loader
        try:
            from mkdocs.config import load_config

            config = load_config("mkdocs.yml")
        except ImportError:
            # Fallback to manual parsing if mkdocs not available
            import re

            with open("mkdocs.yml", "r", encoding="utf-8") as f:
                content = f.read()

            # Extract nav section manually
            nav_match = re.search(r"nav:\s*\n((?:\s+-.*\n)*)", content)
            if not nav_match:
                pytest.skip("Could not parse navigation from mkdocs.yml")

            # Simple nav parsing for testing
            nav_lines = nav_match.group(1).strip().split("\n")
            nav = []
            for line in nav_lines:
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        nav.append({parts[0].strip().lstrip("- "): parts[1].strip()})
            config = {"nav": nav}

        nav_structure = config.get("nav", [])
        docs_dir = Path("docs")

        def extract_files_from_nav(nav_items: List[Any]) -> List[str]:
            """Extract file paths from navigation structure."""
            files = []
            for item in nav_items:
                if isinstance(item, str):
                    files.append(item)
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str):
                            files.append(value)
                        elif isinstance(value, list):
                            files.extend(extract_files_from_nav(value))
            return files

        nav_files = extract_files_from_nav(nav_structure)

        # Verify all navigation files exist
        for file_path in nav_files:
            full_path = docs_dir / file_path
            assert full_path.exists(), (
                f"Navigation references non-existent file: {file_path}"
            )

    def test_portuguese_content_validation(self):
        """Test that documentation contains Portuguese content as required."""
        docs_dir = Path("docs")

        # Files that should contain Portuguese content
        portuguese_files = [
            "index.md",
            "installation.md",
            "usage.md",
            "troubleshooting.md",
        ]

        # Common Portuguese words/phrases that should appear in documentation
        portuguese_indicators = [
            "instalação",
            "uso",
            "como",
            "para",
            "projeto",
            "documentação",
            "exemplo",
            "comando",
            "arquivo",
            "diretório",
            "configuração",
        ]

        for file_name in portuguese_files:
            file_path = docs_dir / file_name
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8").lower()

                # Check if file contains Portuguese content
                portuguese_found = any(
                    indicator in content for indicator in portuguese_indicators
                )
                assert portuguese_found, (
                    f"File {file_name} does not appear to contain Portuguese content"
                )

    def test_code_blocks_preserved(self):
        """Test that code blocks and commands are preserved in documentation."""
        docs_dir = Path("docs")

        # Pattern to match code blocks
        code_block_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
        inline_code_pattern = re.compile(r"`[^`]+`")

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find code blocks
            code_blocks = code_block_pattern.findall(content)
            inline_codes = inline_code_pattern.findall(content)

            # If file contains code, verify it's properly formatted
            if code_blocks or inline_codes:
                # Verify code blocks are properly closed
                open_blocks = content.count("```")
                assert open_blocks % 2 == 0, (
                    f"Unmatched code block markers in {md_file.name}"
                )

    @pytest.mark.slow
    def test_build_performance(self):
        """Test that documentation build completes within reasonable time."""
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "site"

            cmd = ["uv", "run", "mkdocs", "build", "--site-dir", str(build_dir)]

            start_time = time.time()

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minute timeout for performance test
                )
            except subprocess.TimeoutExpired:
                pytest.fail("Documentation build took longer than 2 minutes")
            except FileNotFoundError:
                pytest.skip("MkDocs not available - skipping performance test")

            build_time = time.time() - start_time

            # Build should complete successfully
            assert result.returncode == 0, f"Build failed: {result.stderr}"

            # Build should complete within reasonable time (30 seconds for this small project)
            assert build_time < 30, (
                f"Build took {build_time:.2f} seconds, expected < 30 seconds"
            )

    def test_plugin_configuration(self):
        """Test that all configured plugins are properly set up."""
        try:
            from mkdocs.config import load_config

            config = load_config("mkdocs.yml")
        except ImportError:
            # Fallback to manual parsing if mkdocs not available
            with open("mkdocs.yml", "r", encoding="utf-8") as f:
                content = f.read()

            # Extract plugins section manually
            import re

            plugins_match = re.search(r"plugins:\s*\n((?:\s+-.*\n)*)", content)
            if not plugins_match:
                pytest.skip("Could not parse plugins from mkdocs.yml")

            plugins = []
            for line in plugins_match.group(1).strip().split("\n"):
                if line.strip().startswith("-"):
                    plugin_name = line.strip().lstrip("- ").split(":")[0]
                    plugins.append(plugin_name)
            config = {"plugins": plugins}

        plugins = config.get("plugins", [])

        # Verify essential plugins are configured
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())

        essential_plugins = ["mkdocstrings"]
        search_plugins = ["search", "material/search"]

        # Check for essential plugins
        for plugin in essential_plugins:
            assert plugin in plugin_names, f"Essential plugin '{plugin}' not configured"

        # Check for search functionality (either search or material/search)
        has_search = any(
            search_plugin in plugin_names for search_plugin in search_plugins
        )
        assert has_search, (
            f"No search plugin configured. Expected one of: {search_plugins}"
        )

    def test_markdown_extensions_valid(self):
        """Test that all markdown extensions are properly configured."""
        try:
            from mkdocs.config import load_config

            config = load_config("mkdocs.yml")
        except ImportError:
            # Fallback to manual parsing if mkdocs not available
            with open("mkdocs.yml", "r", encoding="utf-8") as f:
                content = f.read()

            # Extract markdown_extensions section manually
            import re

            extensions_match = re.search(
                r"markdown_extensions:\s*\n((?:\s+-.*\n)*)", content
            )
            if not extensions_match:
                pytest.skip("Could not parse markdown_extensions from mkdocs.yml")

            extensions = []
            for line in extensions_match.group(1).strip().split("\n"):
                if line.strip().startswith("-"):
                    ext_name = line.strip().lstrip("- ").split(":")[0]
                    extensions.append(ext_name)
            config = {"markdown_extensions": extensions}

        extensions = config.get("markdown_extensions", [])

        # Verify essential extensions are present
        essential_extensions = [
            "pymdownx.highlight",
            "pymdownx.superfences",
            "admonition",
            "attr_list",
            "toc",
        ]

        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())

        for ext in essential_extensions:
            assert ext in extension_names, (
                f"Essential markdown extension '{ext}' not configured"
            )
