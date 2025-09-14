import json
import pathlib
from main import (
    get_page_url,
    save_to_json,
    extract_star_rating,
    process_book_listing,
    process_book_details,
)
from unittest.mock import MagicMock, patch


# GET PAGE URL
def test_get_page_url():
    # Test with a valid URL
    url = "https://example.com"
    expected_output = "https://example.com/catalogue/page-2.html"
    assert get_page_url(url, 2) == expected_output

    # Test with a different page number
    expected_output = "https://example.com/catalogue/page-3.html"
    assert get_page_url(url, 3) == expected_output


# SAVE TO JSON
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


@patch("builtins.open")
def test_save_to_json_permission_error(mock_open):
    """Test save_to_json handles file permission errors."""
    mock_open.side_effect = PermissionError("Permission denied")

    data = [{"name": "John", "age": 30}]

    try:
        save_to_json(data, "test.json")
        assert False, "Expected PermissionError to be raised"
    except PermissionError:
        pass  # Expected behavior


@patch("builtins.open")
def test_save_to_json_io_error(mock_open):
    """Test save_to_json handles I/O errors."""
    mock_open.side_effect = IOError("Disk full")

    data = [{"name": "John", "age": 30}]

    try:
        save_to_json(data, "test.json")
        assert False, "Expected IOError to be raised"
    except IOError:
        pass  # Expected behavior


@patch("json.dump")
@patch("builtins.open")
def test_save_to_json_json_serialization_error(mock_open, mock_json_dump):
    """Test save_to_json handles JSON serialization errors."""
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_json_dump.side_effect = TypeError("Object is not JSON serializable")

    # Create data that would cause JSON serialization issues
    data = [
        {"name": "John", "function": lambda x: x}
    ]  # Functions are not JSON serializable

    try:
        save_to_json(data, "test.json")
        assert False, "Expected TypeError to be raised"
    except TypeError:
        pass  # Expected behavior


def test_save_to_json_unicode_encoding(tmp_path):
    """Test save_to_json handles different encoding scenarios."""
    test_output_dir = pathlib.Path(tmp_path) / "test_output"
    test_output_dir.mkdir()

    # Test data with unicode characters
    data = [
        {"name": "José", "city": "São Paulo"},
        {"name": "François", "city": "Montréal"},
        {"name": "北京", "city": "中国"},
        {"emoji": "🚀📚", "special": "åäö"},
    ]

    output_path = test_output_dir / "unicode_test.json"
    save_to_json(data, str(output_path))

    # Verify the file exists and content is correct
    assert output_path.exists()
    loaded_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded_data == data


def test_save_to_json_large_dataset(tmp_path):
    """Test save_to_json handles large data sets."""
    test_output_dir = pathlib.Path(tmp_path) / "test_output"
    test_output_dir.mkdir()

    # Create a large dataset (1000 books with detailed information)
    large_data = []
    for i in range(1000):
        book = {
            "id": i,
            "title": f"Book Title {i}" * 10,  # Make titles longer
            "description": f"This is a very long description for book {i}. " * 20,
            "price": f"£{i + 10}.99",
            "categories": [f"Category {j}" for j in range(5)],
            "reviews": [f"Review {k} for book {i}" for k in range(10)],
        }
        large_data.append(book)

    output_path = test_output_dir / "large_dataset.json"
    save_to_json(large_data, str(output_path))

    # Verify the file exists and content is correct
    assert output_path.exists()
    loaded_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(loaded_data) == 1000
    assert loaded_data[0]["title"] == "Book Title 0" * 10


def test_save_to_json_empty_data(tmp_path):
    """Test save_to_json handles empty data."""
    test_output_dir = pathlib.Path(tmp_path) / "test_output"
    test_output_dir.mkdir()

    # Test with empty list
    empty_data = []
    output_path = test_output_dir / "empty.json"
    save_to_json(empty_data, str(output_path))

    assert output_path.exists()
    loaded_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded_data == []


def test_save_to_json_none_values(tmp_path):
    """Test save_to_json handles None values in data."""
    test_output_dir = pathlib.Path(tmp_path) / "test_output"
    test_output_dir.mkdir()

    # Test data with None values
    data = [
        {"name": "John", "age": None},
        {"name": None, "age": 25},
        {"name": "Jane", "age": 30, "address": None},
    ]

    output_path = test_output_dir / "none_values.json"
    save_to_json(data, str(output_path))

    assert output_path.exists()
    loaded_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded_data == data


@patch("builtins.open")
def test_save_to_json_file_not_found_error(mock_open):
    """Test save_to_json handles FileNotFoundError."""
    mock_open.side_effect = FileNotFoundError("No such file or directory")

    data = [{"name": "John", "age": 30}]

    try:
        save_to_json(data, "/nonexistent/path/test.json")
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError:
        pass  # Expected behavior


# EXTRACT STAR RATING
def test_extract_star_rating_with_one_star():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating One"})

    result = extract_star_rating(mock_book)
    assert result == 1


def test_extract_star_rating_with_two_stars():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Two"})

    result = extract_star_rating(mock_book)
    assert result == 2


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


def test_extract_star_rating_with_five_stars():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Five"})

    result = extract_star_rating(mock_book)
    assert result == 5


def test_extract_star_rating_missing_element():
    mock_book = MagicMock()
    mock_book.find.return_value = None

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_missing_class_attribute():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={})

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_malformed_class_attribute():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Invalid"})

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_no_regex_match():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "some-other-class"})

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_case_sensitivity_lowercase():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating three"})

    result = extract_star_rating(mock_book)
    assert result == 3


def test_extract_star_rating_case_sensitivity_uppercase():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating FOUR"})

    result = extract_star_rating(mock_book)
    assert result == 4


def test_extract_star_rating_case_sensitivity_mixed():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating TwO"})

    result = extract_star_rating(mock_book)
    assert result == 2


def test_extract_star_rating_unknown_rating_text():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": "star-rating Six"})

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_empty_class():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(attrib={"class": ""})

    result = extract_star_rating(mock_book)
    assert result == 0


def test_extract_star_rating_multiple_classes():
    mock_book = MagicMock()
    mock_book.find.return_value = MagicMock(
        attrib={"class": "star-rating Three additional-class"}
    )

    result = extract_star_rating(mock_book)
    assert result == 3


# PROCESS BOOK LISTING
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


def test_process_book_listing_with_invalid_url():
    mock_book = MagicMock()
    mock_book.find.return_value = None

    result = process_book_listing(mock_book, "https://example.com")
    assert result == {}


def test_process_book_listing_with_invalid_image():
    mock_book = MagicMock()

    # Mock the URL element with href and title attributes
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock the price element
    price_element = MagicMock()
    price_element.text = "£19.99"

    # Mock the stock element (using css method)
    mock_book.css.return_value = [" In stock (20 available) "]

    # Mock the star rating element
    star_rating = MagicMock()
    star_rating.attrib = {"class": "star-rating Three"}

    # Set up the mock to return our elements in the correct order
    mock_book.find.side_effect = [
        url_element,  # h3 > a (URL element)
        price_element,  # div.product_price > p.price_color
        None,
    ]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com")

        assert result == {
            "title": "Test Book Title",
            "price": "£19.99",
            "stock_available": "In stock (20 available)",
            "star_rating": 3,
            "image_url": "",
            "detail_url": "https://example.com/catalogue/test-book_1/index.html",
        }


def test_process_book_listing_missing_price_element():
    """Test process_book_listing handles missing price elements."""
    mock_book = MagicMock()

    # Mock the URL element
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock the stock element
    mock_book.css.return_value = [" In stock (20 available) "]

    # Mock the image element
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    # Set up the mock to return elements, with None for price
    mock_book.find.side_effect = [
        url_element,  # h3 > a (URL element)
        None,  # div.product_price > p.price_color (missing)
        image_element,  # div.image_container img
    ]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com")

        assert result == {
            "title": "Test Book Title",
            "price": "",
            "stock_available": "In stock (20 available)",
            "star_rating": 3,
            "image_url": "https://example.com/media/cache/test.jpg",
            "detail_url": "https://example.com/catalogue/test-book_1/index.html",
        }


def test_process_book_listing_malformed_price_data():
    """Test process_book_listing handles malformed price data."""
    mock_book = MagicMock()

    # Mock the URL element
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock the price element with no text attribute
    price_element = MagicMock()
    price_element.text = None

    # Mock the stock element
    mock_book.css.return_value = [" In stock (20 available) "]

    # Mock the image element
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [
        url_element,
        price_element,
        image_element,
    ]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com")

        # The actual code returns None when price_element.text is None, not empty string
        assert result["price"] is None


def test_process_book_listing_missing_stock_information():
    """Test process_book_listing handles missing stock information."""
    mock_book = MagicMock()

    # Mock the URL element
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock the price element
    price_element = MagicMock()
    price_element.text = "£19.99"

    # Mock empty stock information
    mock_book.css.return_value = []

    # Mock the image element
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [
        url_element,
        price_element,
        image_element,
    ]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com")

        assert result["stock_available"] == ""


def test_process_book_listing_various_stock_formats():
    """Test process_book_listing handles various stock formats."""
    test_cases = [
        ([" In stock (5 available) "], "In stock (5 available)"),
        ([" Out of stock "], "Out of stock"),
        (["In stock"], "In stock"),
        (
            [" Available ", " (10 left) "],
            "Available  (10 left)",
        ),  # Note: join() preserves spaces
        ([], ""),
    ]

    for stock_css_return, expected_stock in test_cases:
        mock_book = MagicMock()

        # Mock the URL element
        url_element = MagicMock()
        url_element.attrib = {
            "href": "test-book_1/index.html",
            "title": "Test Book Title",
        }

        # Mock the price element
        price_element = MagicMock()
        price_element.text = "£19.99"

        # Mock the stock element with different formats
        mock_book.css.return_value = stock_css_return

        # Mock the image element
        image_element = MagicMock()
        image_element.attrib = {"src": "media/cache/test.jpg"}

        mock_book.find.side_effect = [
            url_element,
            price_element,
            image_element,
        ]

        with patch("main.extract_star_rating", return_value=3):
            result = process_book_listing(mock_book, "https://example.com")
            assert result["stock_available"] == expected_stock


def test_process_book_listing_relative_url():
    """Test process_book_listing handles relative URLs correctly."""
    mock_book = MagicMock()

    # Mock the URL element with relative URL
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "£19.99"
    mock_book.css.return_value = [" In stock "]
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert (
            result["detail_url"]
            == "https://example.com/catalogue/test-book_1/index.html"
        )


def test_process_book_listing_absolute_url():
    """Test process_book_listing handles absolute URLs correctly."""
    mock_book = MagicMock()

    # Mock the URL element with absolute URL that already contains catalogue
    url_element = MagicMock()
    url_element.attrib = {
        "href": "catalogue/test-book_1/index.html",
        "title": "Test Book Title",
    }

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "£19.99"
    mock_book.css.return_value = [" In stock "]
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert (
            result["detail_url"]
            == "https://example.com/catalogue/test-book_1/index.html"
        )


def test_process_book_listing_malformed_url():
    """Test process_book_listing handles malformed URLs."""
    mock_book = MagicMock()

    # Mock the URL element with empty href
    url_element = MagicMock()
    url_element.attrib = {"title": "Test Book Title"}  # Missing href

    # Mock other elements that would be called
    price_element = MagicMock()
    price_element.text = "£19.99"
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]
    mock_book.css.return_value = [" In stock "]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert result["detail_url"] == "https://example.com/catalogue/"


def test_process_book_listing_special_characters_in_title():
    """Test process_book_listing handles special characters in titles."""
    mock_book = MagicMock()

    # Mock the URL element with special characters in title
    url_element = MagicMock()
    url_element.attrib = {
        "href": "test-book_1/index.html",
        "title": "Test Book: A Story of Love & War (2nd Edition) — Special Characters! @#$%",
    }

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "£19.99"
    mock_book.css.return_value = [" In stock "]
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert (
            result["title"]
            == "Test Book: A Story of Love & War (2nd Edition) — Special Characters! @#$%"
        )


def test_process_book_listing_unicode_characters():
    """Test process_book_listing handles unicode characters in data fields."""
    mock_book = MagicMock()

    # Mock the URL element with unicode characters
    url_element = MagicMock()
    url_element.attrib = {
        "href": "test-book_1/index.html",
        "title": "José's Book: São Paulo Adventures 北京 🚀📚",
    }

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "€19.99"  # Euro symbol
    mock_book.css.return_value = [" En stock (disponible) "]  # French text
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert result["title"] == "José's Book: São Paulo Adventures 北京 🚀📚"
        assert result["price"] == "€19.99"
        assert result["stock_available"] == "En stock (disponible)"


def test_process_book_listing_missing_title_attribute():
    """Test process_book_listing handles missing title attribute."""
    mock_book = MagicMock()

    # Mock the URL element without title attribute
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html"}  # Missing title

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "£19.99"
    mock_book.css.return_value = [" In stock "]
    image_element = MagicMock()
    image_element.attrib = {"src": "media/cache/test.jpg"}

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert result["title"] == ""


def test_process_book_listing_missing_image_src():
    """Test process_book_listing handles missing image src attribute."""
    mock_book = MagicMock()

    # Mock the URL element
    url_element = MagicMock()
    url_element.attrib = {"href": "test-book_1/index.html", "title": "Test Book Title"}

    # Mock other elements
    price_element = MagicMock()
    price_element.text = "£19.99"
    mock_book.css.return_value = [" In stock "]

    # Mock image element without src attribute
    image_element = MagicMock()
    image_element.attrib = {}  # Missing src

    mock_book.find.side_effect = [url_element, price_element, image_element]

    with patch("main.extract_star_rating", return_value=3):
        result = process_book_listing(mock_book, "https://example.com/")

        assert result["image_url"] == "https://example.com/"


# PROCESS BOOK DETAILS
def test_process_book_details():
    test_data = {
        "title": "Test Book Title",
        "price": "£19.99",
        "stock_available": "In stock (20 available)",
        "star_rating": 3,
        "image_url": "https://example.com/media/cache/2c/4a/2c4a8fe7b2f4e5d07a0a0b199a7cc372.jpg",
        "detail_url": "https://example.com/catalogue/test-book_1/index.html",
    }

    detail_page_mock = MagicMock()
    detail_page_mock.find_all.return_value = [
        MagicMock(css=lambda x: MagicMock(text="Test Book Title")),
        MagicMock(css=lambda x: MagicMock(text="£19.99")),
        MagicMock(css=lambda x: MagicMock(text="In stock (20 available)")),
        MagicMock(css=lambda x: MagicMock(text="3")),
        MagicMock(
            css=lambda x: MagicMock(
                text="https://example.com/media/cache/2c/4a/2c4a8fe7b2f4e5d07a0a0b199a7cc372.jpg"
            )
        ),
    ]
    detail_page_mock.status = 200

    with patch("main.Fetcher.get", return_value=detail_page_mock):
        result = process_book_details(test_data)
    assert result == test_data


def test_process_book_details_no_detail_url():
    pass


def test_process_book_details_status_not_200():
    pass
