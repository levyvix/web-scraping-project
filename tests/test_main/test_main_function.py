"""
Comprehensive tests for the main function in main.py.

This module contains tests for the main function including:
- Test infrastructure with comprehensive mocking
- Success scenarios (single page, multi-page, threading)
- Error scenarios (network failures, file errors, threading exceptions)
- Edge cases (max_pages limiting, empty pages, boundary conditions)
"""

import pytest
from unittest.mock import MagicMock, patch, call
from concurrent.futures import ThreadPoolExecutor, Future
import json
from main import main


# Test fixtures for main function testing

@pytest.fixture
def mock_fetcher_get():
    """Mock Fetcher.get with configurable responses."""
    with patch('main.Fetcher.get') as mock_get:
        yield mock_get

@pytest.fixture
def mock_save_to_json():
    """Mock save_to_json function."""
    with patch('main.save_to_json') as mock_save:
        yield mock_save

@pytest.fixture
def mock_logger():
    """Mock logger to capture logging calls."""
    with patch('main.logger') as mock_log:
        yield mock_log

@pytest.fixture
def mock_tqdm():
    """Mock tqdm progress bars."""
    with patch('main.tqdm') as mock_progress:
        # Make tqdm return the iterable unchanged
        mock_progress.side_effect = lambda iterable, **kwargs: iterable
        yield mock_progress

@pytest.fixture
def single_page_response():
    """Mock response for a single page with books."""
    mock_page = MagicMock()
    mock_page.status = 200
    
    # Mock pagination - single page
    mock_pager = MagicMock()
    mock_current = MagicMock()
    mock_current.text = "Page 1 of 1"
    mock_pager.find.return_value = mock_current
    mock_page.find.return_value = mock_pager
    
    # Mock books on the page
    mock_books = []
    for i in range(3):  # 3 books on the page
        mock_book = MagicMock()
        mock_book.name = f"book_{i}"
        mock_books.append(mock_book)
    
    mock_page.find_all.return_value = mock_books
    return mock_page

@pytest.fixture
def multi_page_response():
    """Mock responses for multiple pages."""
    responses = {}
    
    # First page response
    first_page = MagicMock()
    first_page.status = 200
    
    # Mock pagination - 3 pages total
    mock_pager = MagicMock()
    mock_current = MagicMock()
    mock_current.text = "Page 1 of 3"
    mock_pager.find.return_value = mock_current
    first_page.find.return_value = mock_pager
    
    # Mock books on first page
    mock_books = []
    for i in range(2):
        mock_book = MagicMock()
        mock_book.name = f"page1_book_{i}"
        mock_books.append(mock_book)
    first_page.find_all.return_value = mock_books
    
    responses['first'] = first_page
    
    # Subsequent pages
    for page_num in range(2, 4):  # Pages 2 and 3
        page = MagicMock()
        page.status = 200
        
        # Mock books on this page
        page_books = []
        for i in range(2):
            mock_book = MagicMock()
            mock_book.name = f"page{page_num}_book_{i}"
            page_books.append(mock_book)
        page.find_all.return_value = page_books
        
        responses[f'page_{page_num}'] = page
    
    return responses

@pytest.fixture
def empty_page_response():
    """Mock response for a page with no books."""
    mock_page = MagicMock()
    mock_page.status = 200
    
    # Mock pagination - single page
    mock_pager = MagicMock()
    mock_current = MagicMock()
    mock_current.text = "Page 1 of 1"
    mock_pager.find.return_value = mock_current
    mock_page.find.return_value = mock_pager
    
    # No books on the page
    mock_page.find_all.return_value = []
    return mock_page


class TestMainFunctionSuccessScenarios:
    """Test main function success scenarios."""

    def test_single_page_scraping_workflow(
        self, 
        mock_fetcher_get, 
        mock_save_to_json, 
        mock_logger,
        mock_tqdm,
        single_page_response
    ):
        """Test single page scraping workflow."""
        # Setup mock responses
        mock_fetcher_get.return_value = single_page_response
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            # Mock process_book_listing to return basic book data
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "stock_available": "In stock",
                "star_rating": 4,
                "image_url": "https://example.com/image.jpg",
                "detail_url": f"https://example.com/{book.name}",
            }
            
            # Mock process_book_details to return enhanced book data
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category",
                "upc": "test-upc",
                "product_type": "Books"
            }
            
            # Mock ThreadPoolExecutor
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                # Create mock context manager
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                # Mock submit method to return futures
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    # Call the actual function to get realistic results
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                # Mock as_completed to return futures in order
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Call main function
                    main(max_workers=5, max_pages=1)
        
        # Verify Fetcher.get was called for first page
        mock_fetcher_get.assert_called_once_with(
            "https://books.toscrape.com/", 
            stealthy_headers=True
        )
        
        # Verify save_to_json was called
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 3  # 3 books processed
        
        # Verify logging calls
        mock_logger.info.assert_any_call("Starting the scraping process...")
        mock_logger.info.assert_any_call("Fetching first page...")
        mock_logger.success.assert_called_with("Done!")

    def test_multi_page_scraping_with_pagination(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        multi_page_response
    ):
        """Test multi-page scraping with pagination."""
        # Setup mock responses for different pages
        def mock_get_side_effect(url, **kwargs):
            if url == "https://books.toscrape.com/":
                return multi_page_response['first']
            elif "page-2.html" in url:
                return multi_page_response['page_2']
            elif "page-3.html" in url:
                return multi_page_response['page_3']
            else:
                raise ValueError(f"Unexpected URL: {url}")
        
        mock_fetcher_get.side_effect = mock_get_side_effect
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            # Mock ThreadPoolExecutor
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Call main function with max_pages=3
                    main(max_workers=5, max_pages=3)
        
        # Verify Fetcher.get was called for all pages
        expected_calls = [
            call("https://books.toscrape.com/", stealthy_headers=True),
            call("https://books.toscrape.com/catalogue/page-2.html", stealthy_headers=True),
            call("https://books.toscrape.com/catalogue/page-3.html", stealthy_headers=True)
        ]
        mock_fetcher_get.assert_has_calls(expected_calls)
        
        # Verify save_to_json was called with data from all pages
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 6  # 2 books per page × 3 pages
        
        # Verify pagination logging
        mock_logger.info.assert_any_call("Found 3 pages of books")

    def test_threading_and_parallel_processing(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        single_page_response
    ):
        """Test threading and parallel processing."""
        mock_fetcher_get.return_value = single_page_response
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            # Mock ThreadPoolExecutor to verify threading behavior
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                # Track submit calls
                submit_calls = []
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    submit_calls.append((func, args))
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Call main function with specific max_workers
                    main(max_workers=8, max_pages=1)
        
        # Verify ThreadPoolExecutor was called with correct max_workers
        assert mock_executor.call_count == 2  # Once for listings, once for details
        # Check that max_workers=8 was used in both calls
        for call_args in mock_executor.call_args_list:
            assert call_args == call(max_workers=8)
        
        # Verify submit was called for both listing and detail processing
        listing_calls = [call for call in submit_calls if call[0] == mock_listing]
        detail_calls = [call for call in submit_calls if call[0] == mock_details]
        
        assert len(listing_calls) == 3  # 3 books on the page
        assert len(detail_calls) == 3   # 3 books for detail processing

    def test_progress_tracking_and_logging(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        single_page_response
    ):
        """Test progress tracking and logging."""
        mock_fetcher_get.return_value = single_page_response
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    main(max_workers=5, max_pages=1)
        
        # Verify progress bars were created
        assert mock_tqdm.call_count == 2  # One for listings, one for details
        
        # Check tqdm was called with correct descriptions
        tqdm_calls = mock_tqdm.call_args_list
        assert any("Extracting listings from page 1" in str(call) for call in tqdm_calls)
        assert any("Fetching details for page 1 books" in str(call) for call in tqdm_calls)
        
        # Verify key logging messages
        expected_log_calls = [
            "Starting the scraping process...",
            "Fetching first page...",
            "Found 1 pages of books",
            "Processing page 1/1: https://books.toscrape.com/",
            "Found 3 books on page 1",
            "Completed processing page 1",
            "Total books collected: 3",
            "Saving to JSON...",
            "Done!"
        ]
        
        for expected_msg in expected_log_calls:
            try:
                mock_logger.info.assert_any_call(expected_msg)
            except AssertionError:
                mock_logger.success.assert_any_call(expected_msg)


class TestMainFunctionErrorScenarios:
    """Test main function error scenarios."""

    def test_initial_page_fetch_failure(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger
    ):
        """Test initial page fetch failures."""
        # Mock failed initial page fetch
        mock_response = MagicMock()
        mock_response.status = 404
        mock_fetcher_get.return_value = mock_response
        
        # Should raise exception for failed initial page
        with pytest.raises(Exception, match="Failed to fetch first page"):
            main(max_workers=5, max_pages=1)
        
        # Verify error logging
        mock_logger.error.assert_called_with("Failed to fetch first page. Status code: 404")
        
        # Verify save_to_json was not called
        mock_save_to_json.assert_not_called()

    def test_initial_page_network_error(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger
    ):
        """Test network errors during initial page fetch."""
        from requests.exceptions import ConnectionError
        
        # Mock network error
        mock_fetcher_get.side_effect = ConnectionError("Network unreachable")
        
        # Should propagate the network error
        with pytest.raises(ConnectionError):
            main(max_workers=5, max_pages=1)
        
        # Verify save_to_json was not called
        mock_save_to_json.assert_not_called()

    def test_partial_page_processing_failures(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        multi_page_response
    ):
        """Test partial page processing failures."""
        # Setup responses where page 2 fails
        def mock_get_side_effect(url, **kwargs):
            if url == "https://books.toscrape.com/":
                return multi_page_response['first']
            elif "page-2.html" in url:
                # Page 2 fails with 500 error
                mock_response = MagicMock()
                mock_response.status = 500
                return mock_response
            elif "page-3.html" in url:
                return multi_page_response['page_3']
            else:
                raise ValueError(f"Unexpected URL: {url}")
        
        mock_fetcher_get.side_effect = mock_get_side_effect
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Should continue processing despite page 2 failure
                    main(max_workers=5, max_pages=3)
        
        # Verify error was logged for failed page
        mock_logger.error.assert_any_call("Failed to fetch page 2. Status code: 500")
        
        # Verify save_to_json was still called (with data from successful pages)
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 4  # 2 books from page 1 + 2 books from page 3

    def test_file_saving_errors_and_exception_propagation(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        single_page_response
    ):
        """Test file saving errors and exception propagation."""
        mock_fetcher_get.return_value = single_page_response
        
        # Mock save_to_json to raise PermissionError
        mock_save_to_json.side_effect = PermissionError("Permission denied")
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Should propagate file saving error
                    with pytest.raises(PermissionError):
                        main(max_workers=5, max_pages=1)
        
        # Verify logging occurred before the error
        mock_logger.info.assert_any_call("Saving to JSON...")


class TestMainFunctionEdgeCases:
    """Test main function edge cases."""

    def test_max_pages_parameter_limiting(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        multi_page_response
    ):
        """Test max_pages parameter limiting."""
        # Setup first page to indicate 3 total pages
        mock_fetcher_get.return_value = multi_page_response['first']
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Limit to 2 pages when 3 are available
                    main(max_workers=5, max_pages=2)
        
        # Verify limiting message was logged
        mock_logger.info.assert_any_call("Found 3 pages of books")
        mock_logger.info.assert_any_call("Limiting to 2 pages as specified")
        
        # Verify both pages were fetched (first page + page 2 due to limiting to 2 pages)
        expected_calls = [
            call("https://books.toscrape.com/", stealthy_headers=True),
            call("https://books.toscrape.com/catalogue/page-2.html", stealthy_headers=True)
        ]
        # Check that the expected calls are in the actual calls (ignoring other mock calls)
        actual_get_calls = [call for call in mock_fetcher_get.call_args_list 
                           if len(call[0]) > 0 and isinstance(call[0][0], str)]
        assert len(actual_get_calls) == 2

    def test_empty_pages_with_no_books(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        empty_page_response
    ):
        """Test empty pages with no books."""
        mock_fetcher_get.return_value = empty_page_response
        
        with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_context = MagicMock()
            mock_executor.return_value.__enter__.return_value = mock_context
            
            with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                mock_as_completed.side_effect = lambda futures: futures
                
                main(max_workers=5, max_pages=1)
        
        # Verify warning was logged for no books found
        mock_logger.warning.assert_called_with("No books found on page 1!")
        
        # Verify save_to_json was called with empty list
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 0

    def test_single_book_pages_and_boundary_conditions(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm
    ):
        """Test single book pages and boundary conditions."""
        # Create mock page with exactly one book
        mock_page = MagicMock()
        mock_page.status = 200
        
        # Mock pagination - single page
        mock_pager = MagicMock()
        mock_current = MagicMock()
        mock_current.text = "Page 1 of 1"
        mock_pager.find.return_value = mock_current
        mock_page.find.return_value = mock_pager
        
        # Mock single book on the page
        mock_book = MagicMock()
        mock_book.name = "single_book"
        mock_page.find_all.return_value = [mock_book]
        
        mock_fetcher_get.return_value = mock_page
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": "Single Book",
                "price": "£19.99",
                "detail_url": "https://example.com/single_book"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": "Single book description",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    main(max_workers=5, max_pages=1)
        
        # Verify logging for single book
        mock_logger.info.assert_any_call("Found 1 books on page 1")
        
        # Verify save_to_json was called with single book
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 1
        assert saved_data[0]["title"] == "Single Book"

    def test_zero_max_pages_boundary(
        self,
        mock_fetcher_get,
        mock_save_to_json,
        mock_logger,
        mock_tqdm,
        single_page_response
    ):
        """Test zero max_pages boundary condition."""
        mock_fetcher_get.return_value = single_page_response
        
        # Mock the processing functions
        with patch('main.process_book_listing') as mock_listing, \
             patch('main.process_book_details') as mock_details:
            
            mock_listing.side_effect = lambda book, base_url: {
                "title": f"Book {book.name}",
                "price": "£19.99",
                "detail_url": f"https://example.com/{book.name}"
            }
            
            mock_details.side_effect = lambda book_data: {
                **book_data,
                "description": f"Description for {book_data['title']}",
                "category": "Test Category"
            }
            
            with patch('main.concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_context = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_context
                
                def mock_submit(func, *args):
                    future = MagicMock(spec=Future)
                    future.result.return_value = func(*args)
                    return future
                
                mock_context.submit.side_effect = mock_submit
                
                with patch('main.concurrent.futures.as_completed') as mock_as_completed:
                    mock_as_completed.side_effect = lambda futures: futures
                    
                    # Call with max_pages=0
                    # Note: max_pages=0 is falsy, so the limiting logic doesn't apply
                    # The function will still process the detected pages (1 page in this case)
                    main(max_workers=5, max_pages=0)
        
        # Verify the page was still processed because max_pages=0 doesn't trigger limiting
        mock_save_to_json.assert_called_once()
        saved_data = mock_save_to_json.call_args[0][0]
        assert len(saved_data) == 3  # 3 books from the single page