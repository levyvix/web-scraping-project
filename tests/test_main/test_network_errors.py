"""
Network error handling tests for the web scraping project.
Task 9.1: Test network error scenarios
"""

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import ConnectionError, Timeout, HTTPError

from main import process_book_details, main


def test_process_book_details_connection_error():
    """Test process_book_details handles ConnectionError gracefully."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        book_data = {
            "title": "Test Book",
            "price": "£19.99",
            "detail_url": "https://books.toscrape.com/catalogue/test-book_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data unchanged when network fails
        assert result == book_data
        mock_get.assert_called_once_with(
            "https://books.toscrape.com/catalogue/test-book_1/index.html",
            stealthy_headers=True
        )


def test_process_book_details_timeout_error():
    """Test process_book_details handles Timeout gracefully."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = Timeout("Request timeout after 30 seconds")
        
        book_data = {
            "title": "Timeout Test Book",
            "price": "£25.50",
            "detail_url": "https://books.toscrape.com/catalogue/timeout-book_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data unchanged when timeout occurs
        assert result == book_data
        mock_get.assert_called_once()


def test_process_book_details_http_error():
    """Test process_book_details handles HTTPError gracefully."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = HTTPError("404 Client Error: Not Found")
        
        book_data = {
            "title": "HTTP Error Book",
            "price": "£15.75",
            "detail_url": "https://books.toscrape.com/catalogue/http-error-book_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data unchanged when HTTP error occurs
        assert result == book_data


def test_process_book_details_generic_exception():
    """Test process_book_details handles generic exceptions gracefully."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = Exception("Unexpected error occurred")
        
        book_data = {
            "title": "Generic Error Book",
            "price": "£12.99",
            "detail_url": "https://books.toscrape.com/catalogue/generic-error-book_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data unchanged when generic error occurs
        assert result == book_data


def test_main_function_initial_page_connection_error():
    """Test main function handles ConnectionError on initial page fetch."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        # The main function doesn't catch network errors, they propagate up
        with pytest.raises(ConnectionError, match="Network unreachable"):
            main(max_workers=5, max_pages=1)
        
        mock_get.assert_called_once_with("https://books.toscrape.com/", stealthy_headers=True)


def test_main_function_initial_page_timeout():
    """Test main function handles Timeout on initial page fetch."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = Timeout("Request timeout")
        
        # The main function doesn't catch timeout errors, they propagate up
        with pytest.raises(Timeout, match="Request timeout"):
            main(max_workers=5, max_pages=1)


def test_main_function_initial_page_http_error():
    """Test main function handles HTTPError on initial page fetch."""
    with patch('main.Fetcher.get') as mock_get:
        mock_get.side_effect = HTTPError("500 Internal Server Error")
        
        # The main function doesn't catch HTTP errors, they propagate up
        with pytest.raises(HTTPError, match="500 Internal Server Error"):
            main(max_workers=5, max_pages=1)


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 502, 503, 504])
def test_process_book_details_various_http_status_codes(status_code):
    """Test process_book_details handles various HTTP status codes."""
    with patch('main.Fetcher.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = status_code
        mock_get.return_value = mock_response
        
        book_data = {
            "title": f"HTTP {status_code} Book",
            "price": "£20.00",
            "detail_url": f"https://books.toscrape.com/catalogue/http-{status_code}-book_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data unchanged for non-200 status codes
        assert result == book_data


def test_malformed_response_parsing_errors():
    """Test handling of malformed responses that cause parsing errors."""
    with patch('main.Fetcher.get') as mock_get:
        # Mock response that causes parsing errors
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.find.side_effect = Exception("Parsing error")
        mock_response.find_all.side_effect = Exception("Parsing error")
        
        mock_get.return_value = mock_response
        
        book_data = {
            "title": "Parsing Error Book",
            "detail_url": "https://books.toscrape.com/catalogue/parsing-error_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should return original data when parsing fails
        assert result == book_data


def test_network_intermittency_simulation():
    """Test handling of intermittent network issues."""
    with patch('main.Fetcher.get') as mock_get:
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Every second call fails
                raise ConnectionError("Intermittent network error")
            else:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.find_all.return_value = []
                mock_response.find.return_value = None
                return mock_response
        
        mock_get.side_effect = side_effect
        
        # Test multiple book details processing
        book_data_list = [
            {"title": f"Book {i}", "detail_url": f"https://books.toscrape.com/book_{i}.html"}
            for i in range(4)
        ]
        
        results = []
        for book_data in book_data_list:
            result = process_book_details(book_data)
            results.append(result)
        
        # Should handle intermittent failures gracefully
        assert len(results) == 4
        # Some should succeed (with empty additional fields), some should return original data
        for result in results:
            assert "title" in result

# Data Processing Edge Cases Tests - Task 9.2

def test_extract_star_rating_special_characters_in_class():
    """Test extract_star_rating with special characters in class attributes."""
    from main import extract_star_rating
    
    mock_book = MagicMock()
    mock_star_element = MagicMock()
    mock_star_element.attrib = {"class": "star-rating Thr33 & Special!"}
    mock_book.find.return_value = mock_star_element
    
    result = extract_star_rating(mock_book)
    
    # Should return 0 for invalid rating text with special characters
    assert result == 0


def test_extract_star_rating_unicode_characters():
    """Test extract_star_rating with unicode characters in class."""
    from main import extract_star_rating
    
    mock_book = MagicMock()
    mock_star_element = MagicMock()
    mock_star_element.attrib = {"class": "star-rating Thrée"}  # Unicode character
    mock_book.find.return_value = mock_star_element
    
    result = extract_star_rating(mock_book)
    
    # Should return 0 for invalid rating text with unicode characters
    assert result == 0


def test_extract_star_rating_extremely_long_class_string():
    """Test extract_star_rating with extremely long class string."""
    from main import extract_star_rating
    
    mock_book = MagicMock()
    mock_star_element = MagicMock()
    # Create extremely long class string - the regex expects exactly one space after "star-rating"
    long_class = "some-class star-rating Three other-class " + "a" * 10000
    mock_star_element.attrib = {"class": long_class}
    mock_book.find.return_value = mock_star_element
    
    result = extract_star_rating(mock_book)
    
    # Should still extract rating correctly from long string
    assert result == 3


def test_process_book_listing_special_characters_in_title():
    """Test process_book_listing with special characters in title."""
    from main import process_book_listing
    
    mock_book = MagicMock()
    
    # Mock URL element with special characters in title
    mock_url_element = MagicMock()
    mock_url_element.attrib = {
        "href": "test-book_1/index.html",
        "title": "Test Book with Special Chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"
    }
    
    # Mock other elements
    mock_price_element = MagicMock()
    mock_price_element.text = "£19.99"
    mock_image_element = MagicMock()
    mock_image_element.attrib = {"src": "media/test.jpg"}
    
    # Mock star rating element
    mock_star_element = MagicMock()
    mock_star_element.attrib = {"class": "star-rating Three"}
    
    # Set up the find method to return different elements based on selector
    def mock_find(selector):
        if selector == "h3 > a":
            return mock_url_element
        elif selector == "div.product_price > p.price_color":
            return mock_price_element
        elif selector == "div.image_container img":
            return mock_image_element
        elif selector == "p.star-rating":
            return mock_star_element
        return None
    
    mock_book.find.side_effect = mock_find
    mock_book.css.return_value = [" In stock "]
    
    result = process_book_listing(mock_book, "https://books.toscrape.com/")
    
    # Should handle special characters in title
    assert "Test Book with Special Chars" in result["title"]
    assert result["price"] == "£19.99"


def test_process_book_listing_extremely_long_title():
    """Test process_book_listing with extremely long title."""
    from main import process_book_listing
    
    mock_book = MagicMock()
    
    # Create extremely long title
    long_title = "A" * 5000 + " Very Long Book Title"
    
    mock_url_element = MagicMock()
    mock_url_element.attrib = {
        "href": "test-book_1/index.html",
        "title": long_title
    }
    
    mock_price_element = MagicMock()
    mock_price_element.text = "£19.99"
    mock_image_element = MagicMock()
    mock_image_element.attrib = {"src": "media/test.jpg"}
    
    mock_star_element = MagicMock()
    mock_star_element.attrib = {"class": "star-rating Four"}
    
    def mock_find(selector):
        if selector == "h3 > a":
            return mock_url_element
        elif selector == "div.product_price > p.price_color":
            return mock_price_element
        elif selector == "div.image_container img":
            return mock_image_element
        elif selector == "p.star-rating":
            return mock_star_element
        return None
    
    mock_book.find.side_effect = mock_find
    mock_book.css.return_value = [" In stock "]
    
    result = process_book_listing(mock_book, "https://books.toscrape.com/")
    
    # Should handle extremely long title
    assert len(result["title"]) > 5000
    assert "Very Long Book Title" in result["title"]


def test_process_book_listing_empty_and_null_data():
    """Test process_book_listing with empty and null data scenarios."""
    from main import process_book_listing
    
    mock_book = MagicMock()
    
    # Mock elements with empty/null data
    mock_url_element = MagicMock()
    mock_url_element.attrib = {"href": "", "title": ""}
    
    mock_price_element = MagicMock()
    mock_price_element.text = ""
    
    mock_image_element = MagicMock()
    mock_image_element.attrib = {"src": ""}
    
    def mock_find(selector):
        if selector == "h3 > a":
            return mock_url_element
        elif selector == "div.product_price > p.price_color":
            return mock_price_element
        elif selector == "div.image_container img":
            return mock_image_element
        elif selector == "p.star-rating":
            return None  # Missing star rating
        return None
    
    mock_book.find.side_effect = mock_find
    mock_book.css.return_value = [""]
    
    result = process_book_listing(mock_book, "https://books.toscrape.com/")
    
    # Should handle empty data gracefully
    assert result["title"] == ""
    assert result["price"] == ""
    assert result["image_url"] == "https://books.toscrape.com/"
    assert result["star_rating"] == 0


def test_save_to_json_special_characters_and_encoding():
    """Test save_to_json with special characters and encoding issues."""
    import tempfile
    import json
    from pathlib import Path
    from main import save_to_json
    
    test_data = [
        {
            "title": "Book with Unicode: café, naïve, résumé, 中文, العربية, русский",
            "price": "£19.99",
            "description": "Special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`",
            "unicode_field": "🚀📚💻🌟⭐️🎉"
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        save_to_json(test_data, temp_filename)
        
        # Verify file was created and contains correct data
        with open(temp_filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        assert len(loaded_data) == 1
        assert "café" in loaded_data[0]["title"]
        assert "🚀" in loaded_data[0]["unicode_field"]
        
    finally:
        # Clean up
        Path(temp_filename).unlink(missing_ok=True)


def test_save_to_json_extremely_large_data():
    """Test save_to_json with extremely large data sets."""
    import tempfile
    from pathlib import Path
    from main import save_to_json
    
    # Create large dataset
    large_data = []
    for i in range(1000):
        large_data.append({
            "title": f"Book {i} with long description " + "x" * 1000,
            "price": f"£{i}.99",
            "large_field": "y" * 10000
        })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        save_to_json(large_data, temp_filename)
        
        # Verify file was created
        assert Path(temp_filename).exists()
        file_size = Path(temp_filename).stat().st_size
        assert file_size > 1000000  # Should be > 1MB
        
    finally:
        # Clean up
        Path(temp_filename).unlink(missing_ok=True)


def test_save_to_json_malformed_json_serialization():
    """Test save_to_json with data that causes JSON serialization errors."""
    import tempfile
    import datetime
    from pathlib import Path
    from main import save_to_json
    
    # Data with non-serializable objects
    problematic_data = [
        {
            "title": "Test Book",
            "date": datetime.datetime.now(),  # Not JSON serializable
            "function": lambda x: x,  # Not JSON serializable
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_filename = tmp_file.name
    
    try:
        # Should raise TypeError for non-serializable data
        with pytest.raises(TypeError):
            save_to_json(problematic_data, temp_filename)
            
    finally:
        # Clean up
        Path(temp_filename).unlink(missing_ok=True)


def test_save_to_json_file_permission_errors():
    """Test save_to_json with file permission errors."""
    from main import save_to_json
    
    # Try to write to a directory that doesn't exist or has no permissions
    invalid_path = "/root/nonexistent/directory/test.json"
    
    test_data = [{"title": "Test Book", "price": "£19.99"}]
    
    # Should raise PermissionError or FileNotFoundError
    with pytest.raises((PermissionError, FileNotFoundError, OSError)):
        save_to_json(test_data, invalid_path)


def test_process_book_details_encoding_issues_in_response():
    """Test process_book_details with encoding issues in response content."""
    with patch('main.Fetcher.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Mock elements with encoding issues
        mock_description = MagicMock()
        mock_description.text.strip.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
        
        mock_response.find.return_value = mock_description
        mock_response.find_all.return_value = []
        
        mock_get.return_value = mock_response
        
        book_data = {
            "title": "Encoding Issues Book",
            "detail_url": "https://books.toscrape.com/catalogue/encoding-issues_1/index.html"
        }
        
        result = process_book_details(book_data)
        
        # Should handle encoding issues gracefully
        assert "title" in result
        assert result["title"] == "Encoding Issues Book"