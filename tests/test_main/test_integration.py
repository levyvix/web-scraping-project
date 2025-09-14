"""
Integration tests for component interactions in the web scraping project.

These tests verify the data flow between functions and ensure proper
integration of all components in the scraping pipeline.
"""

from unittest.mock import MagicMock, patch

import main


class TestDataFlowIntegration:
    """Test data flow between functions in the scraping pipeline."""

    def test_book_listing_to_detail_processing_pipeline(self, mock_book_listing_page, mock_book_detail_page):
        """Test the complete pipeline from book listing extraction to detail processing."""
        base_url = "https://books.toscrape.com/"
        
        # Mock the Fetcher.get calls
        with patch('main.Fetcher.get') as mock_get:
            # Setup mock responses
            listing_response = MagicMock()
            listing_response.status = 200
            listing_response.find_all.return_value = self._create_mock_book_elements()
            
            detail_response = MagicMock()
            detail_response.status = 200
            detail_response.find_all.return_value = self._create_mock_table_rows()
            detail_response.find.side_effect = [
                self._create_mock_description_element(),
                self._create_mock_breadcrumb_element()
            ]
            
            mock_get.side_effect = [listing_response, detail_response]
            
            # Extract book from listing
            books = listing_response.find_all("li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"})
            book_data = main.process_book_listing(books[0], base_url)
            
            # Verify basic book data structure
            assert "title" in book_data
            assert "price" in book_data
            assert "stock_available" in book_data
            assert "star_rating" in book_data
            assert "image_url" in book_data
            assert "detail_url" in book_data
            
            # Process book details
            enhanced_book_data = main.process_book_details(book_data)
            
            # Verify enhanced data includes additional fields
            assert "upc" in enhanced_book_data
            assert "product_type" in enhanced_book_data
            assert "price_excl_tax" in enhanced_book_data
            assert "price_incl_tax" in enhanced_book_data
            assert "tax" in enhanced_book_data
            assert "availability" in enhanced_book_data
            assert "number_of_reviews" in enhanced_book_data
            assert "description" in enhanced_book_data
            assert "category" in enhanced_book_data
            
            # Verify original data is preserved
            assert enhanced_book_data["title"] == book_data["title"]
            assert enhanced_book_data["price"] == book_data["price"]
            assert enhanced_book_data["star_rating"] == book_data["star_rating"]

    def test_data_transformation_and_enhancement_flow(self):
        """Test how data is transformed and enhanced through the pipeline."""
        base_url = "https://books.toscrape.com/"
        
        # Initial book data (simulating listing extraction)
        initial_data = {
            "title": "Test Book",
            "price": "£25.99",
            "stock_available": "In stock",
            "star_rating": 4,
            "image_url": "https://books.toscrape.com/media/cache/test.jpg",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html"
        }
        
        with patch('main.Fetcher.get') as mock_get:
            # Mock detail page response
            detail_response = MagicMock()
            detail_response.status = 200
            detail_response.find_all.return_value = [
                self._create_mock_table_row("UPC", "abc123def456"),
                self._create_mock_table_row("Product Type", "Books"),
                self._create_mock_table_row("Price (excl. tax)", "£25.99"),
                self._create_mock_table_row("Price (incl. tax)", "£25.99"),
                self._create_mock_table_row("Tax", "£0.00"),
                self._create_mock_table_row("Availability", "In stock (15 available)"),
                self._create_mock_table_row("Number of reviews", "3")
            ]
            
            description_element = MagicMock()
            description_element.text = "This is a test book description."
            
            breadcrumb_element = MagicMock()
            category_link = MagicMock()
            category_link.css.return_value = ["Fiction"]
            breadcrumb_element.find_all.return_value = [None, None, category_link]
            
            detail_response.find.side_effect = [description_element, breadcrumb_element]
            mock_get.return_value = detail_response
            
            # Process the book details
            enhanced_data = main.process_book_details(initial_data)
            
            # Verify data transformation
            assert enhanced_data["upc"] == "abc123def456"
            assert enhanced_data["product_type"] == "Books"
            assert enhanced_data["description"] == "This is a test book description."
            assert enhanced_data["category"] == "Fiction"
            
            # Verify original data is preserved and not corrupted
            assert enhanced_data["title"] == initial_data["title"]
            assert enhanced_data["price"] == initial_data["price"]
            assert enhanced_data["star_rating"] == initial_data["star_rating"]

    def test_error_propagation_between_components(self):
        """Test how errors propagate through the component chain."""
        base_url = "https://books.toscrape.com/"
        
        # Test error in listing processing
        with patch('main.Fetcher.get') as mock_get:
            # Mock a book element with missing required fields
            mock_book = MagicMock()
            mock_book.find.return_value = None  # No URL element found
            
            result = main.process_book_listing(mock_book, base_url)
            
            # Should return empty dict when critical data is missing
            assert result == {}
        
        # Test error propagation in detail processing
        book_data_with_no_url = {
            "title": "Test Book",
            "price": "£25.99",
            "stock_available": "In stock",
            "star_rating": 4,
            "image_url": "https://books.toscrape.com/media/cache/test.jpg",
            # Missing detail_url
        }
        
        result = main.process_book_details(book_data_with_no_url)
        
        # Should return original data when detail URL is missing
        assert result == book_data_with_no_url
        
        # Test network error propagation
        book_data_with_url = {
            "title": "Test Book",
            "price": "£25.99",
            "stock_available": "In stock",
            "star_rating": 4,
            "image_url": "https://books.toscrape.com/media/cache/test.jpg",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html"
        }
        
        with patch('main.Fetcher.get') as mock_get:
            # Simulate network error
            mock_get.side_effect = Exception("Network error")
            
            result = main.process_book_details(book_data_with_url)
            
            # Should return original data when network error occurs
            assert result == book_data_with_url

    def test_star_rating_integration_with_book_processing(self):
        """Test star rating extraction integration with book processing."""
        base_url = "https://books.toscrape.com/"
        
        # Test different star ratings through the pipeline
        star_ratings = ["One", "Two", "Three", "Four", "Five"]
        expected_values = [1, 2, 3, 4, 5]
        
        for rating_text, expected_value in zip(star_ratings, expected_values):
            mock_book = MagicMock()
            
            # Mock URL element
            url_element = MagicMock()
            url_element.attrib = {
                "href": "catalogue/test-book_1/index.html",
                "title": f"Test Book {rating_text}"
            }
            
            # Mock price element
            price_element = MagicMock()
            price_element.text = "£25.99"
            
            # Mock image element
            image_element = MagicMock()
            image_element.attrib = {"src": "media/cache/test.jpg"}
            
            # Mock star rating element
            star_element = MagicMock()
            star_element.attrib = {"class": f"star-rating {rating_text}"}
            
            mock_book.find.side_effect = [url_element, price_element, image_element, star_element]
            mock_book.css.return_value = [" In stock "]
            
            result = main.process_book_listing(mock_book, base_url)
            
            assert result["star_rating"] == expected_value
            assert result["title"] == f"Test Book {rating_text}"

    def test_url_generation_integration_with_pagination(self):
        """Test URL generation integration with pagination processing."""
        base_url = "https://books.toscrape.com/"
        
        # Test page 1 (should return base URL)
        page_1_url = main.get_page_url(base_url, 1)
        assert page_1_url == base_url
        
        # Test other pages
        for page_num in range(2, 6):
            page_url = main.get_page_url(base_url, page_num)
            expected_url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
            assert page_url == expected_url
        
        # Test integration with pagination parsing
        mock_page = MagicMock()
        pager_element = MagicMock()
        current_element = MagicMock()
        current_element.text = "Page 3 of 10"
        pager_element.find.return_value = current_element
        mock_page.find.return_value = pager_element
        
        total_pages = main.get_total_pages(mock_page, base_url)
        assert total_pages == 10
        
        # Generate URLs for all pages
        urls = [main.get_page_url(base_url, page) for page in range(1, total_pages + 1)]
        
        assert urls[0] == base_url  # Page 1
        assert urls[1] == "https://books.toscrape.com/catalogue/page-2.html"  # Page 2
        assert urls[9] == "https://books.toscrape.com/catalogue/page-10.html"  # Page 10

    def _create_mock_book_elements(self):
        """Create mock book elements for testing."""
        book = MagicMock()
        
        # Mock URL element
        url_element = MagicMock()
        url_element.attrib = {
            "href": "catalogue/test-book_1/index.html",
            "title": "Test Book"
        }
        
        # Mock price element
        price_element = MagicMock()
        price_element.text = "£25.99"
        
        # Mock image element
        image_element = MagicMock()
        image_element.attrib = {"src": "media/cache/test.jpg"}
        
        # Mock star rating element
        star_element = MagicMock()
        star_element.attrib = {"class": "star-rating Three"}
        
        book.find.side_effect = [url_element, price_element, image_element, star_element]
        book.css.return_value = [" In stock "]
        
        return [book]

    def _create_mock_table_rows(self):
        """Create mock table rows for detail page."""
        return [
            self._create_mock_table_row("UPC", "abc123def456"),
            self._create_mock_table_row("Product Type", "Books"),
            self._create_mock_table_row("Price (excl. tax)", "£25.99"),
            self._create_mock_table_row("Price (incl. tax)", "£25.99"),
            self._create_mock_table_row("Tax", "£0.00"),
            self._create_mock_table_row("Availability", "In stock (15 available)"),
            self._create_mock_table_row("Number of reviews", "3")
        ]

    def _create_mock_table_row(self, header, value):
        """Create a mock table row element."""
        row = MagicMock()
        row.css.side_effect = [
            [header],  # th::text
            [value]    # td::text
        ]
        return row

    def _create_mock_description_element(self):
        """Create mock description element."""
        element = MagicMock()
        element.text = "This is a test book description."
        return element

    def _create_mock_breadcrumb_element(self):
        """Create mock breadcrumb element."""
        breadcrumb = MagicMock()
        category_link = MagicMock()
        category_link.css.return_value = ["Fiction"]
        breadcrumb.find_all.return_value = [None, None, category_link]
        return breadcrumb


class TestConcurrentProcessingIntegration:
    """Test concurrent processing integration and thread safety."""

    def test_threadpool_executor_integration_with_book_processing(self):
        """Test ThreadPoolExecutor integration with book processing functions."""
        import concurrent.futures
        
        # Test data
        book_data_list = [
            {"title": "Book 1", "detail_url": "https://example.com/book1"},
            {"title": "Book 2", "detail_url": "https://example.com/book2"},
        ]
        
        with patch('main.Fetcher.get') as mock_get:
            # Mock successful detail page responses
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.find_all.return_value = []
            mock_response.find.return_value = None
            mock_get.return_value = mock_response
            
            # Test concurrent processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(main.process_book_details, book_data)
                    for book_data in book_data_list
                ]
                
                results = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
                
                # Verify all books were processed
                assert len(results) == 2
                assert all("title" in result for result in results)

    def test_save_to_json_integration_with_processed_data(self):
        """Test save_to_json integration with processed book data."""
        import tempfile
        import json
        import os
        
        # Test data that would come from the processing pipeline
        processed_books = [
            {
                "title": "Test Book 1",
                "price": "£25.99",
                "star_rating": 4,
                "upc": "abc123",
                "description": "Test description 1"
            },
            {
                "title": "Test Book 2", 
                "price": "£30.50",
                "star_rating": 5,
                "upc": "def456",
                "description": "Test description 2"
            }
        ]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # Test save_to_json function
            main.save_to_json(processed_books, temp_filename)
            
            # Verify file was created and contains correct data
            assert os.path.exists(temp_filename)
            
            with open(temp_filename, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert len(saved_data) == 2
            assert saved_data[0]["title"] == "Test Book 1"
            assert saved_data[1]["title"] == "Test Book 2"
            assert saved_data[0]["star_rating"] == 4
            assert saved_data[1]["star_rating"] == 5
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_pagination_and_url_generation_integration(self):
        """Test integration between pagination parsing and URL generation."""
        base_url = "https://books.toscrape.com/"
        
        # Mock page with pagination info
        mock_page = MagicMock()
        pager_element = MagicMock()
        current_element = MagicMock()
        current_element.text = "Page 2 of 5"
        pager_element.find.return_value = current_element
        mock_page.find.return_value = pager_element
        
        # Test pagination parsing
        total_pages = main.get_total_pages(mock_page, base_url)
        assert total_pages == 5
        
        # Test URL generation for all pages
        page_urls = []
        for page_num in range(1, total_pages + 1):
            url = main.get_page_url(base_url, page_num)
            page_urls.append(url)
        
        # Verify URL generation
        assert page_urls[0] == base_url  # Page 1 should be base URL
        assert page_urls[1] == "https://books.toscrape.com/catalogue/page-2.html"
        assert page_urls[4] == "https://books.toscrape.com/catalogue/page-5.html"
        assert len(page_urls) == 5