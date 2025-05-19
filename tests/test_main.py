import json
import pathlib
from main import get_page_url, save_to_json, extract_star_rating, process_book_listing
from unittest.mock import MagicMock, patch


def test_get_page_url():
    # Test with a valid URL
    url = "https://example.com"
    expected_output = "https://example.com/catalogue/page-2.html"
    assert get_page_url(url, 2) == expected_output

    # Test with a different page number
    expected_output = "https://example.com/catalogue/page-3.html"
    assert get_page_url(url, 3) == expected_output


def test_save_to_json(tmp_path: str):
    # Create a test output directory inside the temporary directory
    test_output_dir = pathlib.Path(tmp_path) / "test_output"
    print(f"test_output_dir: {test_output_dir}")
    test_output_dir.mkdir()

    # Test data
    data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

    # Test 1: Save with default filename in the test output directory
    default_output_path = test_output_dir / "books.json"
    save_to_json(data, str(default_output_path))

    # Verify the file exists
    assert default_output_path.exists()

    # Verify the content
    loaded_data = json.loads(default_output_path.read_text(encoding="utf-8"))
    assert loaded_data == data

    # Test 2: Save with custom filename in the test output directory
    custom_filename = "custom_books.json"
    custom_output_path = test_output_dir / custom_filename
    save_to_json(data, str(custom_output_path))

    # Verify the custom file exists
    assert custom_output_path.exists()

    # Verify the content
    loaded_custom_data = json.loads(custom_output_path.read_text(encoding="utf-8"))
    assert loaded_custom_data == data


def test_extract_star_rating_with_three_stars():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Three"})

    result = extract_star_rating(mock_book)
    assert result == 3


def test_extract_star_rating_with_four_stars():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Four"})

    result = extract_star_rating(mock_book)
    assert result == 4


def test_process_book_listing():
    # Create a mock book element that mimics the structure of a book listing
    mock_book = MagicMock()

    # Mock the URL element with href and title attributes
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock the price element
    price_element = MagicMock()
    price_element.text = "£19.99"

    # Mock the stock element (using css method)
    mock_book.css.return_value = [" In stock (20 available) "]

    # Mock the image element
    image_element = MagicMock()
    image_element.attrib = {
        "src": "media/cache/2c/4a/2c4a8fe7b2f4e5d07a0a0b199a7cc372.jpg"
    }

    # Mock the star rating element
    star_rating = MagicMock()
    star_rating.attrib = {"class": "star-rating Three"}

    # Set up the mock to return our elements in the correct order
    mock_book.find.side_effect = [
        url_element,  # h3 > a (URL element)
        price_element,  # div.product_price > p.price_color
        image_element,  # div.image_container img
    ]

    # Mock the star rating extraction
    with patch("main.extract_star_rating", return_value=3) as mock_extract_rating:
        # Call the function with our mock
        base_url = "https://example.com"
        result = process_book_listing(mock_book, base_url)

        # Verify the results
        assert result == {
            "title": "Test Book Title",
            "price": "£19.99",
            "stock_available": "In stock (20 available)",
            "star_rating": 3,
            "image_url": "https://example.com/media/cache/2c/4a/2c4a8fe7b2f4e5d07a0a0b199a7cc372.jpg",
            "detail_url": "https://example.com/catalogue/test-book_1/index.html",
        }

        # Verify the correct find calls were made
        mock_book.find.assert_any_call("h3 > a")
        mock_book.find.assert_any_call("div.product_price > p.price_color")
        mock_book.find.assert_any_call("div.image_container img")

        # Verify css was called for stock availability
        mock_book.css.assert_called_once_with("p.instock.availability::text")

        # Verify extract_star_rating was called with the book
        mock_extract_rating.assert_called_once_with(mock_book)
