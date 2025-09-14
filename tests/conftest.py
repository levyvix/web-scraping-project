"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

# Import test data and mock responses
from tests.fixtures.test_data import (
    EXPECTED_BASIC_BOOK_DATA,
    EXPECTED_DETAILED_BOOK_DATA,
    EXPECTED_SPECIAL_CHARS_BOOK_DATA,
    SAMPLE_BOOKS_LIST,
    STAR_RATING_TEST_CASES,
    URL_GENERATION_TEST_CASES,
    PAGINATION_TEST_CASES,
    CLI_ARGUMENT_TEST_CASES,
    EDGE_CASE_DATA,
    HTTP_STATUS_CODES,
    THREADING_TEST_SCENARIOS,
)

from tests.fixtures.mock_responses import (
    MOCK_INCOMPLETE_DETAIL_PAGE,
    MOCK_MALFORMED_DETAIL_PAGE,
    MOCK_PAGINATION_PAGE_2_OF_10,
    MOCK_NO_PAGINATION_INFO,
    MOCK_MALFORMED_PAGINATION,
    MOCK_SPECIAL_CHARACTERS_PAGE,
    MOCK_SPECIAL_CHARS_DETAIL_PAGE,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test file operations."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_book_listing_page():
    """Mock HTML response for a valid book listing page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>All products | Books to Scrape</title></head>
    <body>
        <div class="container-fluid page">
            <div class="page_inner">
                <section>
                    <div class="row">
                        <aside class="sidebar col-sm-4 col-md-3">
                            <ul class="pager">
                                <li class="current">
                                    Page 1 of 50
                                </li>
                                <li class="next"><a href="catalogue/page-2.html">next</a></li>
                            </ul>
                        </aside>
                        <div class="col-sm-8 col-md-9">
                            <section>
                                <ol class="row">
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                        <article class="product_pod">
                                            <div class="image_container">
                                                <a href="catalogue/a-light-in-the-attic_1000/index.html">
                                                    <img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic" class="thumbnail">
                                                </a>
                                            </div>
                                            <p class="star-rating Three">
                                                <i class="icon-star"></i>
                                            </p>
                                            <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
                                            <div class="product_price">
                                                <p class="price_color">£51.77</p>
                                            </div>
                                            <p class="instock availability">
                                                <i class="icon-ok"></i>
                                                In stock
                                            </p>
                                        </article>
                                    </li>
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                        <article class="product_pod">
                                            <div class="image_container">
                                                <a href="catalogue/tipping-the-velvet_999/index.html">
                                                    <img src="media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg" alt="Tipping the Velvet" class="thumbnail">
                                                </a>
                                            </div>
                                            <p class="star-rating One">
                                                <i class="icon-star"></i>
                                            </p>
                                            <h3><a href="catalogue/tipping-the-velvet_999/index.html" title="Tipping the Velvet">Tipping the Velvet</a></h3>
                                            <div class="product_price">
                                                <p class="price_color">£53.74</p>
                                            </div>
                                            <p class="instock availability">
                                                <i class="icon-ok"></i>
                                                In stock
                                            </p>
                                        </article>
                                    </li>
                                </ol>
                            </section>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_book_detail_page():
    """Mock HTML response for a complete book detail page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>A Light in the Attic | Books to Scrape</title></head>
    <body>
        <div class="container-fluid page">
            <div class="page_inner">
                <ul class="breadcrumb">
                    <li><a href="../index.html">Home</a></li>
                    <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                    <li><a href="../catalogue/category/books/poetry_23/index.html">Poetry</a></li>
                    <li class="active">A Light in the Attic</li>
                </ul>
                <div class="row">
                    <div class="col-sm-6">
                        <div id="product_gallery">
                            <div id="product_gallery_carousel">
                                <img id="product_image" src="../../media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic">
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-6 product_main">
                        <h1>A Light in the Attic</h1>
                        <p class="star-rating Three">
                            <i class="icon-star"></i>
                        </p>
                        <p class="price_color">£51.77</p>
                        <p class="instock availability">
                            <i class="icon-ok"></i>
                            In stock (22 available)
                        </p>
                        <table class="table table-striped">
                            <tr>
                                <th>UPC</th>
                                <td>a897fe39b1053632</td>
                            </tr>
                            <tr>
                                <th>Product Type</th>
                                <td>Books</td>
                            </tr>
                            <tr>
                                <th>Price (excl. tax)</th>
                                <td>£51.77</td>
                            </tr>
                            <tr>
                                <th>Price (incl. tax)</th>
                                <td>£51.77</td>
                            </tr>
                            <tr>
                                <th>Tax</th>
                                <td>£0.00</td>
                            </tr>
                            <tr>
                                <th>Availability</th>
                                <td>In stock (22 available)</td>
                            </tr>
                            <tr>
                                <th>Number of reviews</th>
                                <td>0</td>
                            </tr>
                        </table>
                    </div>
                </div>
                <div class="sub-header">
                    <h2>Product Description</h2>
                </div>
                <div id="product_description" class="sub-header">
                    <h2>Product Description</h2>
                </div>
                <p>It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative poems have been beloved by generations of kids and adults. This is a book that families can read together for years to come.</p>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_empty_page():
    """Mock HTML response for an empty page with no books."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>All products | Books to Scrape</title></head>
    <body>
        <div class="container-fluid page">
            <div class="page_inner">
                <section>
                    <div class="row">
                        <aside class="sidebar col-sm-4 col-md-3">
                            <ul class="pager">
                                <li class="current">
                                    Page 1 of 1
                                </li>
                            </ul>
                        </aside>
                        <div class="col-sm-8 col-md-9">
                            <section>
                                <ol class="row">
                                    <!-- No books here -->
                                </ol>
                            </section>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_malformed_page():
    """Mock HTML response for a malformed page with missing elements."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Malformed Page</title></head>
    <body>
        <div class="container-fluid page">
            <div class="page_inner">
                <section>
                    <div class="row">
                        <div class="col-sm-8 col-md-9">
                            <section>
                                <ol class="row">
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                        <article class="product_pod">
                                            <!-- Missing image container -->
                                            <!-- Missing star rating -->
                                            <h3><a title="Book Without URL">Book Without URL</a></h3>
                                            <!-- Missing price -->
                                            <!-- Missing stock info -->
                                        </article>
                                    </li>
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                        <article class="product_pod">
                                            <div class="image_container">
                                                <a href="catalogue/incomplete-book_1/index.html">
                                                    <!-- Missing img tag -->
                                                </a>
                                            </div>
                                            <p class="star-rating InvalidRating">
                                                <i class="icon-star"></i>
                                            </p>
                                            <h3><a href="catalogue/incomplete-book_1/index.html" title="Incomplete Book">Incomplete Book</a></h3>
                                            <div class="product_price">
                                                <!-- Missing price_color class -->
                                                <p>£25.00</p>
                                            </div>
                                            <!-- Missing availability info -->
                                        </article>
                                    </li>
                                </ol>
                            </section>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_single_page():
    """Mock HTML response for a single page (no pagination)."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Single Page | Books to Scrape</title></head>
    <body>
        <div class="container-fluid page">
            <div class="page_inner">
                <section>
                    <div class="row">
                        <div class="col-sm-8 col-md-9">
                            <section>
                                <ol class="row">
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                        <article class="product_pod">
                                            <div class="image_container">
                                                <a href="catalogue/single-book_1/index.html">
                                                    <img src="media/cache/single.jpg" alt="Single Book" class="thumbnail">
                                                </a>
                                            </div>
                                            <p class="star-rating Five">
                                                <i class="icon-star"></i>
                                            </p>
                                            <h3><a href="catalogue/single-book_1/index.html" title="Single Book">Single Book</a></h3>
                                            <div class="product_price">
                                                <p class="price_color">£10.00</p>
                                            </div>
                                            <p class="instock availability">
                                                <i class="icon-ok"></i>
                                                In stock
                                            </p>
                                        </article>
                                    </li>
                                </ol>
                            </section>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def expected_book_data():
    """Expected book data structure for testing."""
    return EXPECTED_BASIC_BOOK_DATA.copy()


@pytest.fixture
def expected_detailed_book_data():
    """Expected detailed book data structure after processing detail page."""
    return EXPECTED_DETAILED_BOOK_DATA.copy()


@pytest.fixture
def expected_special_chars_book_data():
    """Expected book data with special characters."""
    return EXPECTED_SPECIAL_CHARS_BOOK_DATA.copy()


@pytest.fixture
def sample_books_list():
    """Sample list of books for testing save_to_json and other functions."""
    return SAMPLE_BOOKS_LIST.copy()


@pytest.fixture
def mock_fetcher_response():
    """Create a mock Fetcher response object."""
    mock_response = MagicMock()
    mock_response.status = 200
    return mock_response


@pytest.fixture
def mock_adaptor():
    """Create a mock Adaptor object for testing."""
    return MagicMock()


@pytest.fixture
def network_error_scenarios():
    """List of network error scenarios for testing."""
    from requests.exceptions import ConnectionError, Timeout, HTTPError

    return [
        ConnectionError("Network unreachable"),
        Timeout("Request timeout"),
        HTTPError("404 Not Found"),
        Exception("Generic network error"),
    ]


@pytest.fixture
def star_rating_test_cases():
    """Test cases for star rating extraction."""
    return STAR_RATING_TEST_CASES.copy()


@pytest.fixture
def url_generation_test_cases():
    """Test cases for URL generation."""
    return URL_GENERATION_TEST_CASES.copy()


@pytest.fixture
def pagination_test_cases():
    """Test cases for pagination parsing."""
    return PAGINATION_TEST_CASES.copy()


@pytest.fixture
def edge_case_data():
    """Edge case data for testing."""
    return EDGE_CASE_DATA.copy()


@pytest.fixture
def http_status_codes():
    """HTTP status codes for testing."""
    return HTTP_STATUS_CODES.copy()


@pytest.fixture
def threading_test_scenarios():
    """Threading test scenarios."""
    return THREADING_TEST_SCENARIOS.copy()


@pytest.fixture
def temp_json_file(temp_dir):
    """Create a temporary JSON file for testing."""
    json_file = temp_dir / "test_books.json"
    return str(json_file)


@pytest.fixture
def mock_book_elements():
    """Create mock book elements for testing process_book_listing."""
    elements = []

    # First book element
    book1 = MagicMock()
    url_element1 = MagicMock()
    url_element1.attrib = {
        "href": "a-light-in-the-attic_1000/index.html",
        "title": "A Light in the Attic",
    }
    price_element1 = MagicMock()
    price_element1.text = "£51.77"
    image_element1 = MagicMock()
    image_element1.attrib = {
        "src": "media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"
    }

    book1.find.side_effect = [url_element1, price_element1, image_element1]
    book1.css.return_value = [" In stock "]
    elements.append(book1)

    # Second book element
    book2 = MagicMock()
    url_element2 = MagicMock()
    url_element2.attrib = {
        "href": "tipping-the-velvet_999/index.html",
        "title": "Tipping the Velvet",
    }
    price_element2 = MagicMock()
    price_element2.text = "£53.74"
    image_element2 = MagicMock()
    image_element2.attrib = {
        "src": "media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg"
    }

    book2.find.side_effect = [url_element2, price_element2, image_element2]
    book2.css.return_value = [" In stock "]
    elements.append(book2)

    return elements


@pytest.fixture
def cli_test_cases():
    """Test cases for CLI argument parsing."""
    return CLI_ARGUMENT_TEST_CASES.copy()


@pytest.fixture
def mock_incomplete_detail_page():
    """Mock HTML response for incomplete book detail page."""
    return MOCK_INCOMPLETE_DETAIL_PAGE


@pytest.fixture
def mock_malformed_detail_page():
    """Mock HTML response for malformed book detail page."""
    return MOCK_MALFORMED_DETAIL_PAGE


@pytest.fixture
def mock_pagination_page():
    """Mock HTML response for pagination page 2 of 10."""
    return MOCK_PAGINATION_PAGE_2_OF_10


@pytest.fixture
def mock_no_pagination_page():
    """Mock HTML response for page with no pagination."""
    return MOCK_NO_PAGINATION_INFO


@pytest.fixture
def mock_malformed_pagination_page():
    """Mock HTML response for page with malformed pagination."""
    return MOCK_MALFORMED_PAGINATION


@pytest.fixture
def mock_special_chars_page():
    """Mock HTML response for page with special characters."""
    return MOCK_SPECIAL_CHARACTERS_PAGE


@pytest.fixture
def mock_special_chars_detail_page():
    """Mock HTML response for book detail with special characters."""
    return MOCK_SPECIAL_CHARS_DETAIL_PAGE


@pytest.fixture
def mock_scrapling_adaptor():
    """Create a mock Scrapling Adaptor object with common methods."""
    mock_adaptor = MagicMock()

    # Mock common methods
    mock_adaptor.find.return_value = None
    mock_adaptor.find_all.return_value = []
    mock_adaptor.css.return_value = []
    mock_adaptor.text = ""
    mock_adaptor.attrib = {}
    mock_adaptor.status = 200

    return mock_adaptor


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with (
        patch("builtins.open"),
        patch("json.dump"),
        patch("json.load"),
        patch("pathlib.Path.exists"),
        patch("pathlib.Path.mkdir"),
    ):
        yield


@pytest.fixture
def mock_network_requests():
    """Mock network requests for testing."""
    with patch("main.Fetcher.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_threading():
    """Mock threading operations for testing."""
    with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
        # Mock the context manager behavior
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        mock_executor.return_value.__exit__.return_value = None

        # Mock submit method to return a future-like object
        mock_future = MagicMock()
        mock_future.result.return_value = {}
        mock_executor_instance.submit.return_value = mock_future

        yield mock_executor_instance
