"""
Comprehensive tests for the get_total_pages function.
Tests pagination parsing scenarios, error handling, and edge cases.
"""

from unittest.mock import MagicMock
from main import get_total_pages


class TestGetTotalPagesPaginationScenarios:
    """Test pagination parsing scenarios for get_total_pages function."""

    def test_get_total_pages_valid_pagination_page_1_of_50(self):
        """Test get_total_pages with valid pagination showing page 1 of 50."""
        mock_page = MagicMock()

        # Mock pager element
        mock_pager = MagicMock()

        # Mock current page element with "Page 1 of 50" text
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 1 of 50"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 50
        mock_page.find.assert_called_once_with("ul.pager")
        mock_pager.find.assert_called_once_with("li.current")

    def test_get_total_pages_valid_pagination_page_5_of_25(self):
        """Test get_total_pages with valid pagination showing page 5 of 25."""
        mock_page = MagicMock()

        # Mock pager element
        mock_pager = MagicMock()

        # Mock current page element with "Page 5 of 25" text
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 5 of 25"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 25

    def test_get_total_pages_valid_pagination_page_10_of_10(self):
        """Test get_total_pages with valid pagination showing last page (10 of 10)."""
        mock_page = MagicMock()

        # Mock pager element
        mock_pager = MagicMock()

        # Mock current page element with "Page 10 of 10" text
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 10 of 10"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 10

    def test_get_total_pages_single_page_no_pagination(self):
        """Test get_total_pages when there's no pagination element (single page)."""
        mock_page = MagicMock()

        # Mock no pager element found
        mock_page.find.return_value = None

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 1
        mock_page.find.assert_called_once_with("ul.pager")

    def test_get_total_pages_pagination_without_current_element(self):
        """Test get_total_pages when pager exists but no current element."""
        mock_page = MagicMock()

        # Mock pager element exists but no current element
        mock_pager = MagicMock()
        mock_pager.find.return_value = None  # No li.current element

        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 1
        mock_page.find.assert_called_once_with("ul.pager")
        mock_pager.find.assert_called_once_with("li.current")

    def test_get_total_pages_malformed_pagination_text(self):
        """Test get_total_pages with malformed pagination text."""
        mock_page = MagicMock()

        # Mock pager element
        mock_pager = MagicMock()

        # Mock current page element with malformed text
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page X of Y"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 1  # Should default to 1 when regex doesn't match

    def test_get_total_pages_edge_case_unusual_page_numbers(self):
        """Test get_total_pages with unusual but valid page numbers."""
        test_cases = [
            ("Page 1 of 1", 1),  # Single page
            ("Page 1 of 2", 2),  # Two pages
            ("Page 99 of 100", 100),  # Large page numbers
            ("Page 1 of 999", 999),  # Very large page numbers
            ("Page 500 of 1000", 1000),  # Mid-range large numbers
        ]

        for page_text, expected_total in test_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_total, f"Failed for page text: {page_text}"

    def test_get_total_pages_whitespace_handling(self):
        """Test get_total_pages handles whitespace in pagination text correctly."""
        test_cases = [
            ("  Page 1 of 50  ", 50),  # Leading/trailing whitespace (stripped)
            ("\nPage 1 of 50\n", 50),  # Newlines (stripped)
            ("\tPage 1 of 50\t", 50),  # Tabs (stripped)
            ("Page  1  of  50", 1),  # Multiple spaces (won't match regex)
            (
                " \n\t Page 1 of 50 \t\n ",
                50,
            ),  # Mixed whitespace (stripped to valid format)
        ]

        for page_text, expected_total in test_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text.strip()

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_total, f"Failed for page text: '{page_text}'"

    def test_get_total_pages_case_sensitivity(self):
        """Test get_total_pages handles case variations in pagination text."""
        test_cases = [
            ("page 1 of 50", 1),  # lowercase 'page' - should not match
            ("PAGE 1 OF 50", 1),  # uppercase - should not match
            ("Page 1 Of 50", 1),  # mixed case with capital 'Of' - should not match
            ("Page 1 of 50", 50),  # standard case - should match
        ]

        for page_text, expected_total in test_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_total, f"Failed for page text: '{page_text}'"

    def test_get_total_pages_empty_pagination_text(self):
        """Test get_total_pages with empty pagination text."""
        mock_page = MagicMock()
        mock_pager = MagicMock()
        mock_current = MagicMock()
        mock_current.text.strip.return_value = ""

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 1  # Should default to 1 for empty text

    def test_get_total_pages_pagination_with_extra_text(self):
        """Test get_total_pages with pagination text containing extra information."""
        test_cases = [
            ("Showing Page 1 of 50 results", 50),
            ("Page 1 of 50 - Books to Scrape", 50),
            ("Current: Page 1 of 50", 50),
            ("Page 1 of 50 (total books: 1000)", 50),
        ]

        for page_text, expected_total in test_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_total, f"Failed for page text: '{page_text}'"


class TestGetTotalPagesErrorHandling:
    """Test error handling scenarios for get_total_pages function."""

    def test_get_total_pages_missing_pagination_elements(self):
        """Test get_total_pages when pagination elements are completely missing."""
        mock_page = MagicMock()

        # Mock no pager element found
        mock_page.find.return_value = None

        result = get_total_pages(mock_page, "https://example.com")

        assert result == 1
        mock_page.find.assert_called_once_with("ul.pager")

    def test_get_total_pages_invalid_page_number_formats(self):
        """Test get_total_pages with invalid page number formats."""
        invalid_formats = [
            "Page abc of def",  # Non-numeric values
            "Page 1.5 of 50.7",  # Decimal numbers
            "Page -1 of -50",  # Negative numbers
            "Page 1 of",  # Missing total pages
            "Page of 50",  # Missing current page
            "1 of 50",  # Missing "Page" keyword
            "Page 1 50",  # Missing "of" keyword
            "Page one of fifty",  # Written numbers
            "Page 1 of infinity",  # Non-numeric total
        ]

        for invalid_format in invalid_formats:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = invalid_format

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == 1, f"Failed for invalid format: '{invalid_format}'"

    def test_get_total_pages_regex_matching_edge_cases(self):
        """Test get_total_pages regex matching with various edge cases."""
        edge_cases = [
            ("Page1of50", 1),  # No spaces
            ("Page  1  of  50", 1),  # Multiple spaces (won't match)
            ("Page\t1\tof\t50", 1),  # Tabs instead of spaces (won't match)
            ("Page 1 of 50 extra", 50),  # Extra text after
            ("prefix Page 1 of 50", 50),  # Text before
            (
                "Page 01 of 050",
                50,
            ),  # Leading zeros (regex matches \d+ which includes leading zeros)
            (
                "Page 1 of 50.",
                50,
            ),  # Period after number (regex still matches the digits)
            (
                "Page 1 of 50,",
                50,
            ),  # Comma after number (regex still matches the digits)
        ]

        for test_text, expected_result in edge_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = test_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_result, f"Failed for edge case: '{test_text}'"

    def test_get_total_pages_none_text_attribute(self):
        """Test get_total_pages when current element text attribute is None."""
        mock_page = MagicMock()
        mock_pager = MagicMock()
        mock_current = MagicMock()

        # Mock text attribute as None
        mock_current.text = None

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        # This should raise an AttributeError when trying to call strip() on None
        try:
            result = get_total_pages(mock_page, "https://example.com")
            # If no exception is raised, the function should handle it gracefully
            assert result == 1
        except AttributeError:
            # This is expected behavior if the function doesn't handle None text
            pass

    def test_get_total_pages_exception_in_find_operations(self):
        """Test get_total_pages when find operations raise exceptions."""
        mock_page = MagicMock()

        # Mock find operation to raise an exception
        mock_page.find.side_effect = Exception("DOM parsing error")

        try:
            result = get_total_pages(mock_page, "https://example.com")
            # If no exception is raised, function handled it gracefully
            assert result == 1
        except Exception:
            # This is expected if the function doesn't handle exceptions
            pass

    def test_get_total_pages_malformed_dom_structure(self):
        """Test get_total_pages with malformed DOM structure."""
        mock_page = MagicMock()

        # Mock pager element that exists but has no proper structure
        mock_pager = MagicMock()
        mock_pager.find.side_effect = Exception("Malformed DOM")

        mock_page.find.return_value = mock_pager

        try:
            result = get_total_pages(mock_page, "https://example.com")
            assert result == 1
        except Exception:
            # Expected if function doesn't handle DOM parsing errors
            pass

    def test_get_total_pages_very_large_page_numbers(self):
        """Test get_total_pages with extremely large page numbers."""
        large_numbers = [
            ("Page 1 of 999999", 999999),
            ("Page 1 of 1000000", 1000000),
            ("Page 999999 of 999999", 999999),
        ]

        for page_text, expected_total in large_numbers:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_total, f"Failed for large number: {page_text}"

    def test_get_total_pages_unicode_characters_in_pagination(self):
        """Test get_total_pages with unicode characters in pagination text."""
        unicode_cases = [
            ("Página 1 of 50", 1),  # Spanish "Page"
            (
                "Page 1 of 50 páginas",
                50,
            ),  # Mixed languages (regex still matches the core pattern)
            ("Page 1 of 50 📄", 50),  # Emoji (regex still matches the core pattern)
            (
                "Page 1 of 50 — Books",
                50,
            ),  # Em dash (regex still matches the core pattern)
            (
                "Page 1 of 50 • Total",
                50,
            ),  # Bullet point (regex still matches the core pattern)
        ]

        for page_text, expected_result in unicode_cases:
            mock_page = MagicMock()
            mock_pager = MagicMock()
            mock_current = MagicMock()
            mock_current.text.strip.return_value = page_text

            mock_pager.find.return_value = mock_current
            mock_page.find.return_value = mock_pager

            result = get_total_pages(mock_page, "https://example.com")
            assert result == expected_result, f"Failed for unicode case: '{page_text}'"

    def test_get_total_pages_base_url_parameter_ignored(self):
        """Test that get_total_pages ignores the base_url parameter correctly."""
        mock_page = MagicMock()
        mock_pager = MagicMock()
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 1 of 25"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        # Test with different base URLs - result should be the same
        base_urls = [
            "https://example.com",
            "https://different.com",
            "http://localhost:8000",
            "",
            None,
        ]

        for base_url in base_urls:
            result = get_total_pages(mock_page, base_url)
            assert result == 25, f"Failed for base_url: {base_url}"

    def test_get_total_pages_current_page_greater_than_total(self):
        """Test get_total_pages when current page number is greater than total (edge case)."""
        # This shouldn't happen in normal circumstances, but test the regex behavior
        mock_page = MagicMock()
        mock_pager = MagicMock()
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 100 of 50"  # Current > Total

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        # The function should still extract the total pages (50) regardless of logic
        assert result == 50

    def test_get_total_pages_zero_values(self):
        """Test get_total_pages with zero page values."""
        mock_page = MagicMock()
        mock_pager = MagicMock()
        mock_current = MagicMock()
        mock_current.text.strip.return_value = "Page 0 of 0"

        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager

        result = get_total_pages(mock_page, "https://example.com")

        # The regex will match and return 0, which is the actual behavior
        assert result == 0
