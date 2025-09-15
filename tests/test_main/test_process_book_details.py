"""
Comprehensive tests for the process_book_details function.
"""

from unittest.mock import MagicMock, patch
from requests.exceptions import ConnectionError, Timeout, HTTPError

from main import process_book_details


class TestProcessBookDetailsSuccessScenarios:
    """Test success scenarios for process_book_details function."""

    @patch("main.Fetcher.get")
    def test_process_complete_detail_page(self, mock_get):
        """Test processing a complete detail page with all fields present."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [
                ("UPC", "complete123456789"),
                ("Product Type", "Books"),
                ("Price (excl. tax)", "£35.99"),
                ("Price (incl. tax)", "£35.99"),
                ("Tax", "£0.00"),
                ("Availability", "In stock (15 available)"),
                ("Number of reviews", "12"),
            ]
        )

        # Mock description element
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "This is a complete book with all fields present. It has a comprehensive description that includes multiple sentences and provides detailed information about the book's content, themes, and target audience. This description is used to test the complete processing of book detail pages."
        mock_response.find.return_value = mock_description

        # Mock breadcrumb for category
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Mystery"]
        mock_breadcrumb.find_all.return_value = [
            None,
            None,
            mock_category_li,
        ]  # Home, Books, Category
        mock_response.find.side_effect = [mock_description, mock_breadcrumb]

        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Complete Book",
            "price": "£35.99",
            "detail_url": "https://books.toscrape.com/catalogue/complete-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify
        assert result["upc"] == "complete123456789"
        assert result["product_type"] == "Books"
        assert result["price_excl_tax"] == "£35.99"
        assert result["price_incl_tax"] == "£35.99"
        assert result["tax"] == "£0.00"
        assert result["availability"] == "In stock (15 available)"
        assert result["number_of_reviews"] == "12"
        assert "comprehensive description" in result["description"]
        assert result["category"] == "Mystery"

        # Verify original data is preserved
        assert result["title"] == "Complete Book"
        assert result["price"] == "£35.99"
        assert (
            result["detail_url"]
            == "https://books.toscrape.com/catalogue/complete-book_1/index.html"
        )

    @patch("main.Fetcher.get")
    def test_process_partial_detail_page_missing_description(self, mock_get):
        """Test processing a detail page with missing description."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [
                ("UPC", "nodesc123"),
                ("Product Type", "Books"),
                ("Price (excl. tax)", "£18.50"),
                ("Price (incl. tax)", "£18.50"),
                ("Tax", "£0.00"),
                ("Availability", "In stock (8 available)"),
                ("Number of reviews", "3"),
            ]
        )

        # Mock missing description element
        mock_response.find.return_value = None  # No description found

        # Mock breadcrumb for category
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Romance"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]
        mock_response.find.side_effect = [
            None,
            mock_breadcrumb,
        ]  # No description, has breadcrumb

        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "No Description Book",
            "price": "£18.50",
            "detail_url": "https://books.toscrape.com/catalogue/no-description-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify
        assert result["upc"] == "nodesc123"
        assert result["product_type"] == "Books"
        assert result["description"] == ""  # Missing description should be empty string
        assert result["category"] == "Romance"

    @patch("main.Fetcher.get")
    def test_process_partial_detail_page_missing_category(self, mock_get):
        """Test processing a detail page with missing category (no breadcrumb)."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [("UPC", "nocat456"), ("Product Type", "Books"), ("Number of reviews", "7")]
        )

        # Mock description element
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "This book has no category information because the breadcrumb navigation is missing."

        # Mock missing breadcrumb
        mock_response.find.side_effect = [
            mock_description,
            None,
        ]  # Has description, no breadcrumb

        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "No Category Book",
            "price": "£42.00",
            "detail_url": "https://books.toscrape.com/catalogue/no-category-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify
        assert result["upc"] == "nocat456"
        assert result["product_type"] == "Books"
        assert result["number_of_reviews"] == "7"
        assert (
            result["description"]
            == "This book has no category information because the breadcrumb navigation is missing."
        )
        assert result["category"] == ""  # Missing category should be empty string

    @patch("main.Fetcher.get")
    def test_breadcrumb_navigation_extraction(self, mock_get):
        """Test breadcrumb navigation and category extraction."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = []  # Empty table for simplicity

        # Mock description
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Test description"

        # Mock breadcrumb with multiple levels
        mock_breadcrumb = MagicMock()
        mock_li_elements = []

        # Create mock li elements for: Home, Books, Fiction, Subcategory
        for i, text in enumerate(["Home", "Books", "Fiction", "Subcategory"]):
            mock_li = MagicMock()
            mock_li.css.return_value = [text]
            mock_li_elements.append(mock_li)

        mock_breadcrumb.find_all.return_value = mock_li_elements
        mock_response.find.side_effect = [mock_description, mock_breadcrumb]

        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Test Book",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify - should extract the third breadcrumb item (index 2)
        assert result["category"] == "Fiction"

    @patch("main.Fetcher.get")
    def test_product_information_table_parsing(self, mock_get):
        """Test product information table parsing with various data types."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200

        # Create comprehensive table data
        table_data = [
            ("UPC", "abc123def456"),
            ("Product Type", "Books"),
            ("Price (excl. tax)", "£29.99"),
            ("Price (incl. tax)", "£29.99"),
            ("Tax", "£0.00"),
            ("Availability", "In stock (42 available)"),
            ("Number of reviews", "15"),
        ]

        mock_response.find_all.return_value = self._create_mock_table_rows(table_data)

        # Mock other elements
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Comprehensive test description"
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Test Category"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Comprehensive Test Book",
            "detail_url": "https://books.toscrape.com/catalogue/comprehensive-test_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify all table fields are correctly parsed
        assert result["upc"] == "abc123def456"
        assert result["product_type"] == "Books"
        assert result["price_excl_tax"] == "£29.99"
        assert result["price_incl_tax"] == "£29.99"
        assert result["tax"] == "£0.00"
        assert result["availability"] == "In stock (42 available)"
        assert result["number_of_reviews"] == "15"

    @patch("main.Fetcher.get")
    def test_process_book_with_special_characters(self, mock_get):
        """Test processing a book detail page with special characters."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [
                ("UPC", "special123&chars"),
                ("Product Type", "Books & Literature"),
                ("Price (excl. tax)", "£99.99"),
                ("Price (incl. tax)", "£99.99"),
                ("Tax", "£0.00"),
                ("Availability", "In stock (1 available)"),
                ("Number of reviews", "5"),
            ]
        )

        # Mock description with special characters
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "This book contains special characters like & (ampersand), quotes 'single' and \"double\", and unicode characters: café, résumé, naïve. It's designed to test edge cases in text processing."

        # Mock breadcrumb with special characters
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Fiction & Literature"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data with special characters
        book_data = {
            "title": "Book with Special & Characters: Quotes 'n' Stuff",
            "price": "£99.99",
            "detail_url": "https://books.toscrape.com/catalogue/special-chars_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify special characters are handled correctly
        assert result["upc"] == "special123&chars"
        assert result["product_type"] == "Books & Literature"
        assert result["category"] == "Fiction & Literature"
        assert "café, résumé, naïve" in result["description"]
        assert "quotes 'single' and \"double\"" in result["description"]

    @patch("main.Fetcher.get")
    def test_process_book_with_unicode_characters(self, mock_get):
        """Test processing a book detail page with unicode characters."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [
                ("UPC", "unicode123北京"),
                ("Product Type", "Books"),
                ("Price (excl. tax)", "£45.67"),
                ("Price (incl. tax)", "£45.67"),
                ("Tax", "£0.00"),
                ("Availability", "En stock (disponible)"),
                ("Number of reviews", "8"),
            ]
        )

        # Mock description with unicode
        mock_description = MagicMock()
        mock_description.text.strip.return_value = (
            "José's adventure in São Paulo with émojis 📚🚀 and special symbols ñáéíóú"
        )

        # Mock breadcrumb with unicode
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Ficción & Literatura"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data with unicode
        book_data = {
            "title": "José's Book: São Paulo Adventures 北京 🚀📚",
            "price": "€45.67",
            "detail_url": "https://books.toscrape.com/catalogue/unicode-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify unicode characters are handled correctly
        assert result["upc"] == "unicode123北京"
        assert result["availability"] == "En stock (disponible)"
        assert result["category"] == "Ficción & Literatura"
        assert "José's adventure" in result["description"]
        assert "📚🚀" in result["description"]

    @patch("main.Fetcher.get")
    def test_process_book_with_minimal_table_data(self, mock_get):
        """Test processing a book with minimal table data (only some fields)."""
        # Setup mock response with only a few table fields
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [("UPC", "minimal123"), ("Number of reviews", "1")]
        )

        # Mock description
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Minimal book description"

        # Mock breadcrumb
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Minimal"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Minimal Book",
            "price": "£10.00",
            "detail_url": "https://books.toscrape.com/catalogue/minimal-book_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify present fields are populated
        assert result["upc"] == "minimal123"
        assert result["number_of_reviews"] == "1"
        assert result["description"] == "Minimal book description"
        assert result["category"] == "Minimal"

        # Verify missing fields are empty strings
        assert result["product_type"] == ""
        assert result["price_excl_tax"] == ""
        assert result["price_incl_tax"] == ""
        assert result["tax"] == ""
        assert result["availability"] == ""

    @patch("main.Fetcher.get")
    def test_process_book_with_long_description(self, mock_get):
        """Test processing a book with a very long description."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [("UPC", "longdesc123"), ("Product Type", "Books")]
        )

        # Create a very long description
        long_description = "This is a very long description. " * 100  # 3400+ characters
        mock_description = MagicMock()
        mock_description.text.strip.return_value = long_description

        # Mock breadcrumb
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Long Books"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Book with Long Description",
            "detail_url": "https://books.toscrape.com/catalogue/long-desc_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify long description is handled correctly
        assert result["description"] == long_description
        assert len(result["description"]) > 3000
        assert result["category"] == "Long Books"

    @patch("main.Fetcher.get")
    def test_process_book_with_complex_breadcrumb(self, mock_get):
        """Test processing a book with complex breadcrumb navigation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = []  # Empty table for simplicity

        # Mock description
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Complex breadcrumb test"

        # Mock complex breadcrumb with many levels
        mock_breadcrumb = MagicMock()
        breadcrumb_levels = [
            "Home",
            "Books",
            "Fiction",
            "Mystery",
            "Crime",
            "Detective",
        ]
        mock_li_elements = []

        for level in breadcrumb_levels:
            mock_li = MagicMock()
            mock_li.css.return_value = [level]
            mock_li_elements.append(mock_li)

        mock_breadcrumb.find_all.return_value = mock_li_elements
        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Complex Breadcrumb Book",
            "detail_url": "https://books.toscrape.com/catalogue/complex-breadcrumb_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify it extracts the third breadcrumb item (index 2)
        assert result["category"] == "Fiction"

    @patch("main.Fetcher.get")
    def test_process_book_with_whitespace_in_data(self, mock_get):
        """Test processing a book with whitespace in table data."""
        # Setup mock response with whitespace in values
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [
                ("UPC", "  whitespace123  "),
                ("Product Type", "\n\tBooks\n\t"),
                ("Price (excl. tax)", "  £25.99  "),
                ("Availability", "\n  In stock (10 available)  \n"),
            ]
        )

        # Mock description with whitespace
        mock_description = MagicMock()
        mock_description.text.strip.return_value = (
            "Description with proper whitespace handling"
        )

        # Mock breadcrumb with whitespace
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["  Category with Spaces  "]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        # Test data
        book_data = {
            "title": "Whitespace Test Book",
            "detail_url": "https://books.toscrape.com/catalogue/whitespace-test_1/index.html",
        }

        # Execute
        result = process_book_details(book_data)

        # Verify whitespace is stripped by the implementation (join().strip())
        assert result["upc"] == "whitespace123"
        assert result["product_type"] == "Books"
        assert result["price_excl_tax"] == "£25.99"
        assert result["availability"] == "In stock (10 available)"
        assert result["category"] == "Category with Spaces"

    def _create_mock_table_rows(self, data_pairs):
        """Helper method to create mock table rows."""
        mock_rows = []
        for header, value in data_pairs:
            mock_row = MagicMock()
            mock_row.css.side_effect = [
                [header],  # th::text
                [value],  # td::text
            ]
            mock_rows.append(mock_row)
        return mock_rows


class TestProcessBookDetailsErrorScenarios:
    """Test error scenarios for process_book_details function."""

    def test_no_detail_url(self):
        """Test process_book_details when no detail URL is provided."""
        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            # Missing detail_url
        }

        result = process_book_details(book_data)

        # Should return original data unchanged
        assert result == book_data

    def test_empty_detail_url(self):
        """Test process_book_details when detail URL is empty."""
        book_data = {"title": "Test Book", "price": "£19.99", "detail_url": ""}

        result = process_book_details(book_data)

        # Should return original data unchanged
        assert result == book_data

    def test_none_detail_url(self):
        """Test process_book_details when detail URL is None."""
        book_data = {"title": "Test Book", "price": "£19.99", "detail_url": None}

        result = process_book_details(book_data)

        # Should return original data unchanged
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_network_connection_error(self, mock_get):
        """Test process_book_details handles ConnectionError."""
        mock_get.side_effect = ConnectionError("Network unreachable")

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when network fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_network_timeout_error(self, mock_get):
        """Test process_book_details handles Timeout."""
        mock_get.side_effect = Timeout("Request timeout")

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when timeout occurs
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_http_error(self, mock_get):
        """Test process_book_details handles HTTPError."""
        mock_get.side_effect = HTTPError("404 Not Found")

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when HTTP error occurs
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_generic_exception(self, mock_get):
        """Test process_book_details handles generic exceptions."""
        mock_get.side_effect = Exception("Generic network error")

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when generic error occurs
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_http_404_status(self, mock_get):
        """Test process_book_details handles 404 HTTP status."""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_get.return_value = mock_response

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when status is not 200
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_http_500_status(self, mock_get):
        """Test process_book_details handles 500 HTTP status."""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_get.return_value = mock_response

        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data unchanged when status is not 200
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_malformed_html_missing_elements(self, mock_get):
        """Test process_book_details handles malformed HTML with missing elements."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Mock empty/missing elements
        mock_response.find_all.return_value = []  # No table rows
        mock_response.find.return_value = None  # No description or breadcrumb

        mock_get.return_value = mock_response

        book_data = {
            "title": "Malformed Page Book",
            "price": "£25.00",
            "detail_url": "https://books.toscrape.com/catalogue/malformed-book_1/index.html",
        }

        result = process_book_details(book_data)

        # Should handle missing elements gracefully
        assert result["upc"] == ""
        assert result["product_type"] == ""
        assert result["price_excl_tax"] == ""
        assert result["price_incl_tax"] == ""
        assert result["tax"] == ""
        assert result["availability"] == ""
        assert result["number_of_reviews"] == ""
        assert result["description"] == ""
        assert result["category"] == ""

        # Original data should be preserved
        assert result["title"] == "Malformed Page Book"
        assert result["price"] == "£25.00"

    @patch("main.Fetcher.get")
    def test_malformed_table_structure(self, mock_get):
        """Test process_book_details handles malformed table structures."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Create malformed table rows
        malformed_rows = []

        # Row with missing th
        row1 = MagicMock()
        row1.css.side_effect = [[], ["malformed789"]]  # Empty th, has td
        malformed_rows.append(row1)

        # Row with missing td
        row2 = MagicMock()
        row2.css.side_effect = [["Product Type"], []]  # Has th, empty td
        malformed_rows.append(row2)

        # Normal row
        row3 = MagicMock()
        row3.css.side_effect = [["Price (excl. tax)"], ["£28.75"]]
        malformed_rows.append(row3)

        # Row with empty values
        row4 = MagicMock()
        row4.css.side_effect = [[""], [""]]  # Empty th and td
        malformed_rows.append(row4)

        mock_response.find_all.return_value = malformed_rows

        # Mock other elements
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Malformed table test"
        mock_breadcrumb = MagicMock()
        mock_category_li = MagicMock()
        mock_category_li.css.return_value = ["Science"]
        mock_breadcrumb.find_all.return_value = [None, None, mock_category_li]

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        book_data = {
            "title": "Malformed Table Book",
            "detail_url": "https://books.toscrape.com/catalogue/malformed-table_1/index.html",
        }

        result = process_book_details(book_data)

        # Should handle malformed table gracefully
        assert result["product_type"] == ""  # Missing td should result in empty string
        assert result["price_excl_tax"] == "£28.75"  # Normal row should work
        assert result["description"] == "Malformed table test"
        assert result["category"] == "Science"

    @patch("main.Fetcher.get")
    def test_exception_during_parsing(self, mock_get):
        """Test process_book_details handles exceptions during HTML parsing."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Mock find_all to raise an exception
        mock_response.find_all.side_effect = Exception("Parsing error")

        mock_get.return_value = mock_response

        book_data = {
            "title": "Parsing Error Book",
            "price": "£30.00",
            "detail_url": "https://books.toscrape.com/catalogue/parsing-error_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when parsing fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_http_status_codes_error_handling(self, mock_get):
        """Test process_book_details handles various HTTP error status codes."""
        error_codes = [400, 401, 403, 404, 500, 502, 503, 504]

        book_data = {
            "title": "HTTP Error Book",
            "price": "£20.00",
            "detail_url": "https://books.toscrape.com/catalogue/http-error_1/index.html",
        }

        for status_code in error_codes:
            mock_response = MagicMock()
            mock_response.status = status_code
            mock_get.return_value = mock_response

            result = process_book_details(book_data)

            # Should return original data unchanged for any non-200 status
            assert result == book_data, f"Failed for status code {status_code}"

    @patch("main.Fetcher.get")
    def test_fetcher_returns_none(self, mock_get):
        """Test process_book_details handles when Fetcher.get returns None."""
        mock_get.return_value = None

        book_data = {
            "title": "None Response Book",
            "price": "£15.00",
            "detail_url": "https://books.toscrape.com/catalogue/none-response_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when response is None
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_response_missing_status_attribute(self, mock_get):
        """Test process_book_details handles response without status attribute."""
        mock_response = MagicMock()
        # Remove status attribute to simulate AttributeError
        del mock_response.status
        mock_get.return_value = mock_response

        book_data = {
            "title": "No Status Book",
            "price": "£22.50",
            "detail_url": "https://books.toscrape.com/catalogue/no-status_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when status attribute is missing
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_find_all_returns_none(self, mock_get):
        """Test process_book_details handles when find_all returns None."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = None  # Instead of empty list
        mock_response.find.return_value = None

        mock_get.return_value = mock_response

        book_data = {
            "title": "Find All None Book",
            "detail_url": "https://books.toscrape.com/catalogue/find-all-none_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when find_all returns None (causes exception)
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_css_method_raises_exception(self, mock_get):
        """Test process_book_details handles exceptions from css method calls."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Create a mock row where css() raises an exception
        mock_row = MagicMock()
        mock_row.css.side_effect = Exception("CSS parsing error")
        mock_response.find_all.return_value = [mock_row]

        # Mock find to also raise exception
        mock_response.find.side_effect = Exception("Find method error")

        mock_get.return_value = mock_response

        book_data = {
            "title": "CSS Error Book",
            "detail_url": "https://books.toscrape.com/catalogue/css-error_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when CSS parsing fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_breadcrumb_find_all_raises_exception(self, mock_get):
        """Test process_book_details handles exceptions from breadcrumb find_all."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = []  # Empty table

        # Mock description works fine
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Test description"

        # Mock breadcrumb that raises exception on find_all
        mock_breadcrumb = MagicMock()
        mock_breadcrumb.find_all.side_effect = Exception("Breadcrumb parsing error")

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        book_data = {
            "title": "Breadcrumb Error Book",
            "detail_url": "https://books.toscrape.com/catalogue/breadcrumb-error_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when breadcrumb parsing fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_description_text_strip_raises_exception(self, mock_get):
        """Test process_book_details handles exceptions from description text.strip()."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find_all.return_value = []  # Empty table

        # Mock description where text.strip() raises exception
        mock_description = MagicMock()
        mock_description.text.strip.side_effect = Exception("Text strip error")

        mock_response.find.side_effect = [
            mock_description,
            None,
        ]  # Description error, no breadcrumb
        mock_get.return_value = mock_response

        book_data = {
            "title": "Description Error Book",
            "detail_url": "https://books.toscrape.com/catalogue/description-error_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when description processing fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_table_row_iteration_error(self, mock_get):
        """Test process_book_details handles errors during table row iteration."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Create a mock that raises exception when iterated
        mock_table_rows = MagicMock()
        mock_table_rows.__iter__.side_effect = Exception("Table iteration error")
        mock_response.find_all.return_value = mock_table_rows

        mock_response.find.return_value = None  # No description or breadcrumb
        mock_get.return_value = mock_response

        book_data = {
            "title": "Table Iteration Error Book",
            "detail_url": "https://books.toscrape.com/catalogue/table-iteration-error_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when table iteration fails
        assert result == book_data

    @patch("main.Fetcher.get")
    def test_graceful_degradation_partial_success(self, mock_get):
        """Test process_book_details graceful degradation with partial success."""
        mock_response = MagicMock()
        mock_response.status = 200

        # Table processing works
        mock_response.find_all.return_value = self._create_mock_table_rows(
            [("UPC", "partial123"), ("Product Type", "Books")]
        )

        # Description works
        mock_description = MagicMock()
        mock_description.text.strip.return_value = "Partial success description"

        # Breadcrumb fails
        mock_breadcrumb = MagicMock()
        mock_breadcrumb.find_all.side_effect = Exception("Breadcrumb error")

        mock_response.find.side_effect = [mock_description, mock_breadcrumb]
        mock_get.return_value = mock_response

        book_data = {
            "title": "Partial Success Book",
            "detail_url": "https://books.toscrape.com/catalogue/partial-success_1/index.html",
        }

        result = process_book_details(book_data)

        # Should return original data when any part fails (due to try-catch around entire block)
        assert result == book_data

    def _create_mock_table_rows(self, data_pairs):
        """Helper method to create mock table rows."""
        mock_rows = []
        for header, value in data_pairs:
            mock_row = MagicMock()
            mock_row.css.side_effect = [
                [header],  # th::text
                [value],  # td::text
            ]
            mock_rows.append(mock_row)
        return mock_rows
