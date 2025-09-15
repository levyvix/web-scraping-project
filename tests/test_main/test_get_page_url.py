"""
Comprehensive tests for the get_page_url function.

This module contains tests covering all URL generation scenarios, edge cases,
and base URL format variations as specified in task 5.1.
"""

from main import get_page_url


class TestGetPageUrlBasicScenarios:
    """Test basic URL generation scenarios."""

    def test_page_1_returns_base_url(self):
        """Test that page 1 URL generation returns the base URL unchanged."""
        base_url = "https://books.toscrape.com/"
        result = get_page_url(base_url, 1)
        assert result == base_url

    def test_page_1_returns_base_url_without_trailing_slash(self):
        """Test that page 1 URL generation returns the base URL unchanged (no trailing slash)."""
        base_url = "https://books.toscrape.com"
        result = get_page_url(base_url, 1)
        assert result == base_url

    def test_various_page_numbers(self):
        """Test URL generation for various page numbers."""
        base_url = "https://books.toscrape.com/"

        test_cases = [
            (2, "https://books.toscrape.com/catalogue/page-2.html"),
            (3, "https://books.toscrape.com/catalogue/page-3.html"),
            (10, "https://books.toscrape.com/catalogue/page-10.html"),
            (50, "https://books.toscrape.com/catalogue/page-50.html"),
            (100, "https://books.toscrape.com/catalogue/page-100.html"),
        ]

        for page_num, expected_url in test_cases:
            result = get_page_url(base_url, page_num)
            assert result == expected_url, f"Failed for page {page_num}"

    def test_large_page_numbers(self):
        """Test URL generation for large page numbers."""
        base_url = "https://books.toscrape.com/"

        test_cases = [
            (999, "https://books.toscrape.com/catalogue/page-999.html"),
            (1000, "https://books.toscrape.com/catalogue/page-1000.html"),
            (9999, "https://books.toscrape.com/catalogue/page-9999.html"),
        ]

        for page_num, expected_url in test_cases:
            result = get_page_url(base_url, page_num)
            assert result == expected_url, f"Failed for page {page_num}"


class TestGetPageUrlBaseUrlEdgeCases:
    """Test base URL edge cases and format variations."""

    def test_base_url_with_trailing_slash(self):
        """Test URL generation with base URL that has trailing slash."""
        base_url = "https://example.com/"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"

    def test_base_url_without_trailing_slash(self):
        """Test URL generation with base URL that has no trailing slash."""
        base_url = "https://example.com"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"

    def test_base_url_with_path(self):
        """Test URL generation with base URL that includes a path."""
        base_url = "https://example.com/books/"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/books/catalogue/page-2.html"

    def test_base_url_with_path_no_trailing_slash(self):
        """Test URL generation with base URL that includes a path without trailing slash."""
        base_url = "https://example.com/books"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"

    def test_base_url_with_subdomain(self):
        """Test URL generation with base URL that includes subdomain."""
        base_url = "https://api.example.com/"
        result = get_page_url(base_url, 3)
        assert result == "https://api.example.com/catalogue/page-3.html"

    def test_base_url_with_port(self):
        """Test URL generation with base URL that includes port number."""
        base_url = "https://example.com:8080/"
        result = get_page_url(base_url, 4)
        assert result == "https://example.com:8080/catalogue/page-4.html"

    def test_base_url_with_query_parameters(self):
        """Test URL generation with base URL that includes query parameters.

        Note: urljoin() doesn't preserve query parameters when joining URLs,
        so they are stripped from the result.
        """
        base_url = "https://example.com/?lang=en"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"

    def test_base_url_with_fragment(self):
        """Test URL generation with base URL that includes fragment.

        Note: urljoin() doesn't preserve fragments when joining URLs,
        so they are stripped from the result.
        """
        base_url = "https://example.com/#section1"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"


class TestGetPageUrlDifferentProtocols:
    """Test URL generation with different protocols."""

    def test_http_protocol(self):
        """Test URL generation with HTTP protocol."""
        base_url = "http://example.com/"
        result = get_page_url(base_url, 2)
        assert result == "http://example.com/catalogue/page-2.html"

    def test_https_protocol(self):
        """Test URL generation with HTTPS protocol."""
        base_url = "https://example.com/"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/catalogue/page-2.html"

    def test_localhost_url(self):
        """Test URL generation with localhost."""
        base_url = "http://localhost:3000/"
        result = get_page_url(base_url, 2)
        assert result == "http://localhost:3000/catalogue/page-2.html"

    def test_ip_address_url(self):
        """Test URL generation with IP address."""
        base_url = "http://192.168.1.100/"
        result = get_page_url(base_url, 2)
        assert result == "http://192.168.1.100/catalogue/page-2.html"


class TestGetPageUrlEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_page_zero(self):
        """Test URL generation for page 0 (should still generate catalogue URL)."""
        base_url = "https://example.com/"
        result = get_page_url(base_url, 0)
        assert result == "https://example.com/catalogue/page-0.html"

    def test_negative_page_number(self):
        """Test URL generation for negative page numbers."""
        base_url = "https://example.com/"
        result = get_page_url(base_url, -1)
        assert result == "https://example.com/catalogue/page--1.html"

    def test_very_long_base_url(self):
        """Test URL generation with very long base URL."""
        base_url = "https://very-long-domain-name-for-testing-purposes.example.com/very/long/path/structure/"
        result = get_page_url(base_url, 2)
        expected = "https://very-long-domain-name-for-testing-purposes.example.com/very/long/path/structure/catalogue/page-2.html"
        assert result == expected

    def test_base_url_with_special_characters(self):
        """Test URL generation with base URL containing special characters."""
        base_url = "https://example.com/books-and-more/"
        result = get_page_url(base_url, 2)
        assert result == "https://example.com/books-and-more/catalogue/page-2.html"

    def test_base_url_with_unicode_domain(self):
        """Test URL generation with internationalized domain name."""
        base_url = "https://bücher.example.com/"
        result = get_page_url(base_url, 2)
        assert result == "https://bücher.example.com/catalogue/page-2.html"


class TestGetPageUrlConsistency:
    """Test consistency and reliability of URL generation."""

    def test_multiple_calls_same_result(self):
        """Test that multiple calls with same parameters return same result."""
        base_url = "https://example.com/"
        page_num = 5

        results = [get_page_url(base_url, page_num) for _ in range(10)]

        # All results should be identical
        assert all(result == results[0] for result in results)
        assert results[0] == "https://example.com/catalogue/page-5.html"

    def test_different_base_urls_different_results(self):
        """Test that different base URLs produce different results."""
        page_num = 2

        base_urls = [
            "https://example.com/",
            "https://test.com/",
            "https://books.example.org/",
        ]

        results = [get_page_url(base_url, page_num) for base_url in base_urls]

        # All results should be different
        assert len(set(results)) == len(results)

    def test_sequential_page_numbers(self):
        """Test URL generation for sequential page numbers."""
        base_url = "https://example.com/"

        for page_num in range(1, 11):
            result = get_page_url(base_url, page_num)

            if page_num == 1:
                assert result == base_url
            else:
                expected = f"https://example.com/catalogue/page-{page_num}.html"
                assert result == expected


class TestGetPageUrlRealWorldScenarios:
    """Test real-world scenarios and actual usage patterns."""

    def test_books_toscrape_actual_url(self):
        """Test with the actual books.toscrape.com URL."""
        base_url = "https://books.toscrape.com/"

        # Test page 1 (should return base URL)
        result_page_1 = get_page_url(base_url, 1)
        assert result_page_1 == "https://books.toscrape.com/"

        # Test page 2
        result_page_2 = get_page_url(base_url, 2)
        assert result_page_2 == "https://books.toscrape.com/catalogue/page-2.html"

        # Test page 50 (typical pagination scenario)
        result_page_50 = get_page_url(base_url, 50)
        assert result_page_50 == "https://books.toscrape.com/catalogue/page-50.html"

    def test_common_web_scraping_scenarios(self):
        """Test common web scraping URL patterns."""
        test_scenarios = [
            ("https://example-bookstore.com/", 1, "https://example-bookstore.com/"),
            (
                "https://example-bookstore.com/",
                2,
                "https://example-bookstore.com/catalogue/page-2.html",
            ),
            (
                "https://shop.example.com/books/",
                3,
                "https://shop.example.com/books/catalogue/page-3.html",
            ),
            ("http://localhost:8000/", 1, "http://localhost:8000/"),
            (
                "http://localhost:8000/",
                4,
                "http://localhost:8000/catalogue/page-4.html",
            ),
        ]

        for base_url, page_num, expected in test_scenarios:
            result = get_page_url(base_url, page_num)
            assert result == expected, f"Failed for {base_url}, page {page_num}"

    def test_pagination_workflow_simulation(self):
        """Test simulating a typical pagination workflow."""
        base_url = "https://books.toscrape.com/"
        max_pages = 5

        urls = []
        for page_num in range(1, max_pages + 1):
            url = get_page_url(base_url, page_num)
            urls.append(url)

        # Verify the generated URLs
        expected_urls = [
            "https://books.toscrape.com/",
            "https://books.toscrape.com/catalogue/page-2.html",
            "https://books.toscrape.com/catalogue/page-3.html",
            "https://books.toscrape.com/catalogue/page-4.html",
            "https://books.toscrape.com/catalogue/page-5.html",
        ]

        assert urls == expected_urls

        # Verify no duplicates
        assert len(set(urls)) == len(urls)
