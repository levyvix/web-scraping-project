"""
Tests for automated link checking in documentation.

This module contains tests to validate internal links, cross-references,
and ensure all documentation links are working correctly.
"""

import pytest
import re
from pathlib import Path
from typing import List


class TestDocumentationLinks:
    """Test suite for documentation link validation."""

    def test_internal_links_valid(self):
        """Test that all internal markdown links point to existing files."""
        docs_dir = Path("docs")

        # Pattern to match markdown links [text](path)
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        broken_links = []

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find all links in the file
            links = link_pattern.findall(content)

            for link_text, link_path in links:
                # Skip external links (http/https)
                if link_path.startswith(("http://", "https://", "mailto:")):
                    continue

                # Skip anchors within same page
                if link_path.startswith("#"):
                    continue

                # Handle relative paths
                if link_path.startswith("./"):
                    link_path = link_path[2:]

                # Remove anchor fragments
                if "#" in link_path:
                    link_path = link_path.split("#")[0]

                # Check if target file exists
                target_path = docs_dir / link_path
                if not target_path.exists():
                    broken_links.append(
                        {
                            "source_file": md_file.name,
                            "link_text": link_text,
                            "target_path": link_path,
                            "full_target": str(target_path),
                        }
                    )

        if broken_links:
            error_msg = "Found broken internal links:\n"
            for link in broken_links:
                error_msg += f"  - In {link['source_file']}: '{link['link_text']}' -> {link['target_path']}\n"
            pytest.fail(error_msg)

    def test_navigation_links_valid(self):
        """Test that all navigation entries point to existing files."""
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
        broken_nav_links = []

        def check_nav_links(nav_items: List, path_prefix: str = ""):
            """Recursively check navigation links."""
            for item in nav_items:
                if isinstance(item, str):
                    # Direct file reference
                    file_path = docs_dir / item
                    if not file_path.exists():
                        broken_nav_links.append(f"{path_prefix}{item}")
                elif isinstance(item, dict):
                    for title, value in item.items():
                        if isinstance(value, str):
                            # File reference with title
                            file_path = docs_dir / value
                            if not file_path.exists():
                                broken_nav_links.append(
                                    f"{path_prefix}{title} -> {value}"
                                )
                        elif isinstance(value, list):
                            # Nested navigation
                            check_nav_links(value, f"{path_prefix}{title}/")

        check_nav_links(nav_structure)

        if broken_nav_links:
            error_msg = "Found broken navigation links:\n"
            for link in broken_nav_links:
                error_msg += f"  - {link}\n"
            pytest.fail(error_msg)

    def test_cross_references_valid(self):
        """Test that cross-references between documentation pages are valid."""
        docs_dir = Path("docs")

        # Pattern to match various cross-reference formats
        patterns = [
            re.compile(
                r"\[([^\]]+)\]\(([^)]+\.md(?:#[^)]*)?)\)"
            ),  # [text](file.md#anchor)
            re.compile(r"\]\(\.\.?/([^)]+\.md(?:#[^)]*)?)\)"),  # ](../file.md#anchor)
        ]

        broken_refs = []

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            for pattern in patterns:
                matches = pattern.findall(content)

                for match in matches:
                    if isinstance(match, tuple):
                        # Handle tuple results from multiple groups
                        ref_path = match[-1] if len(match) > 1 else match[0]
                    else:
                        ref_path = match

                    # Clean up the path
                    if ref_path.startswith("../"):
                        ref_path = ref_path[3:]
                    elif ref_path.startswith("./"):
                        ref_path = ref_path[2:]

                    # Remove anchor if present
                    file_path = ref_path.split("#")[0] if "#" in ref_path else ref_path

                    # Check if referenced file exists
                    target_file = docs_dir / file_path
                    if not target_file.exists():
                        broken_refs.append(
                            {
                                "source": md_file.name,
                                "reference": ref_path,
                                "target": file_path,
                            }
                        )

        if broken_refs:
            error_msg = "Found broken cross-references:\n"
            for ref in broken_refs:
                error_msg += (
                    f"  - In {ref['source']}: reference to {ref['reference']}\n"
                )
            pytest.fail(error_msg)

    def test_anchor_links_valid(self):
        """Test that anchor links point to existing headers."""
        docs_dir = Path("docs")

        # Pattern to match anchor links
        anchor_pattern = re.compile(r"\[([^\]]+)\]\(([^)]*#[^)]+)\)")
        # Pattern to match headers
        header_pattern = re.compile(r"^#+\s+(.+)$", re.MULTILINE)

        broken_anchors = []

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find all headers in the file
            headers = header_pattern.findall(content)
            # Convert headers to anchor format (lowercase, spaces to hyphens, remove special chars)
            anchors = set()
            for header in headers:
                anchor = re.sub(r"[^\w\s-]", "", header.lower())
                anchor = re.sub(r"[-\s]+", "-", anchor).strip("-")
                anchors.add(anchor)

            # Find all anchor links
            anchor_links = anchor_pattern.findall(content)

            for link_text, link_path in anchor_links:
                # Parse the link
                if "#" in link_path:
                    file_part, anchor_part = link_path.split("#", 1)

                    # If no file part, it's a same-page anchor
                    if not file_part or file_part in (".", "./"):
                        target_anchors = anchors
                        target_file = md_file.name
                    else:
                        # It's a cross-file anchor
                        if file_part.startswith("./"):
                            file_part = file_part[2:]

                        target_path = docs_dir / file_part
                        if target_path.exists():
                            target_content = target_path.read_text(encoding="utf-8")
                            target_headers = header_pattern.findall(target_content)
                            target_anchors = set()
                            for header in target_headers:
                                anchor = re.sub(r"[^\w\s-]", "", header.lower())
                                anchor = re.sub(r"[-\s]+", "-", anchor).strip("-")
                                target_anchors.add(anchor)
                            target_file = file_part
                        else:
                            # File doesn't exist, will be caught by other tests
                            continue

                    # Check if anchor exists
                    if anchor_part not in target_anchors:
                        broken_anchors.append(
                            {
                                "source": md_file.name,
                                "link_text": link_text,
                                "target_file": target_file,
                                "anchor": anchor_part,
                                "available_anchors": sorted(target_anchors),
                            }
                        )

        if broken_anchors:
            error_msg = "Found broken anchor links:\n"
            for anchor in broken_anchors:
                error_msg += f"  - In {anchor['source']}: '{anchor['link_text']}' -> {anchor['target_file']}#{anchor['anchor']}\n"
                if anchor["available_anchors"]:
                    error_msg += f"    Available anchors: {', '.join(anchor['available_anchors'][:5])}\n"
            pytest.fail(error_msg)

    def test_image_links_valid(self):
        """Test that image references point to existing files."""
        docs_dir = Path("docs")

        # Pattern to match image links ![alt](path)
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

        broken_images = []

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find all image links
            images = image_pattern.findall(content)

            for alt_text, image_path in images:
                # Skip external images
                if image_path.startswith(("http://", "https://")):
                    continue

                # Handle relative paths
                if image_path.startswith("./"):
                    image_path = image_path[2:]

                # Check if image file exists
                target_path = docs_dir / image_path
                if not target_path.exists():
                    broken_images.append(
                        {
                            "source_file": md_file.name,
                            "alt_text": alt_text,
                            "image_path": image_path,
                        }
                    )

        if broken_images:
            error_msg = "Found broken image links:\n"
            for img in broken_images:
                error_msg += f"  - In {img['source_file']}: '{img['alt_text']}' -> {img['image_path']}\n"
            pytest.fail(error_msg)

    def test_api_reference_links(self):
        """Test that API reference links are properly formatted."""
        api_ref_file = Path("docs/api-reference.md")

        if not api_ref_file.exists():
            pytest.skip("API reference file not found")

        content = api_ref_file.read_text(encoding="utf-8")

        # Check for mkdocstrings syntax
        mkdocstrings_pattern = re.compile(r"::: (\w+(?:\.\w+)*)")

        api_refs = mkdocstrings_pattern.findall(content)

        if api_refs:
            # Verify that referenced modules/functions exist in the project
            project_files = list(Path(".").glob("*.py")) + list(
                Path(".").glob("**/*.py")
            )

            # Extract available modules
            available_modules = set()
            for py_file in project_files:
                if py_file.name != "__init__.py" and not py_file.name.startswith(
                    "test_"
                ):
                    # Convert file path to module path
                    module_path = (
                        str(py_file.with_suffix(""))
                        .replace("/", ".")
                        .replace("\\", ".")
                    )
                    available_modules.add(module_path)

                    # Also add the file name as a module
                    available_modules.add(py_file.stem)

            missing_refs = []
            for ref in api_refs:
                # Check if the reference matches any available module
                if not any(
                    ref.startswith(module) or module.startswith(ref)
                    for module in available_modules
                ):
                    missing_refs.append(ref)

            if missing_refs:
                error_msg = (
                    "API reference contains references to non-existent modules:\n"
                )
                for ref in missing_refs:
                    error_msg += f"  - {ref}\n"
                error_msg += (
                    f"Available modules: {', '.join(sorted(available_modules))}"
                )
                pytest.fail(error_msg)

    def test_external_links_format(self):
        """Test that external links are properly formatted and not broken internally."""
        docs_dir = Path("docs")

        # Pattern to match external links
        external_link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")

        malformed_links = []

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find all external links
            external_links = external_link_pattern.findall(content)

            for link_text, url in external_links:
                # Basic URL format validation
                if not re.match(r'https?://[^\s<>"{}|\\^`\[\]]+$', url):
                    malformed_links.append(
                        {
                            "source_file": md_file.name,
                            "link_text": link_text,
                            "url": url,
                            "issue": "Invalid URL format",
                        }
                    )

                # Check for common issues
                if url.endswith((".", ",")):
                    malformed_links.append(
                        {
                            "source_file": md_file.name,
                            "link_text": link_text,
                            "url": url,
                            "issue": "URL ends with punctuation",
                        }
                    )

        if malformed_links:
            error_msg = "Found malformed external links:\n"
            for link in malformed_links:
                error_msg += f"  - In {link['source_file']}: '{link['link_text']}' -> {link['url']} ({link['issue']})\n"
            pytest.fail(error_msg)

    def test_link_consistency(self):
        """Test that links to the same target are consistent across documentation."""
        docs_dir = Path("docs")

        # Pattern to match all markdown links
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        # Collect all links
        all_links = {}  # target -> list of (source_file, link_text)

        for md_file in docs_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            links = link_pattern.findall(content)

            for link_text, target in links:
                # Skip external links for this test
                if target.startswith(("http://", "https://", "mailto:")):
                    continue

                # Normalize target path
                normalized_target = target.lower().strip()

                if normalized_target not in all_links:
                    all_links[normalized_target] = []

                all_links[normalized_target].append((md_file.name, link_text))

        # Check for inconsistent link text for same targets
        inconsistent_links = []

        for target, link_instances in all_links.items():
            if len(link_instances) > 1:
                # Get unique link texts for this target
                link_texts = set(link_text for _, link_text in link_instances)

                if len(link_texts) > 1:
                    inconsistent_links.append(
                        {
                            "target": target,
                            "instances": link_instances,
                            "texts": link_texts,
                        }
                    )

        if inconsistent_links:
            error_msg = "Found inconsistent link text for same targets:\n"
            for link in inconsistent_links:
                error_msg += f"  - Target '{link['target']}' has different texts: {', '.join(link['texts'])}\n"
                for source, text in link["instances"]:
                    error_msg += f"    - In {source}: '{text}'\n"
            # This is a warning rather than a failure for now
            pytest.skip(f"Link consistency issues found (non-critical):\n{error_msg}")
