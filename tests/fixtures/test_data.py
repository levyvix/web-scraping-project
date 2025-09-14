"""
Test data fixtures for expected book data structures and test scenarios.
"""

from typing import Dict, List, Any

# Expected book data for basic listing processing
EXPECTED_BASIC_BOOK_DATA = {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "stock_available": "In stock",
    "star_rating": 3,
    "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "detail_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}

# Expected book data after detail processing
EXPECTED_DETAILED_BOOK_DATA = {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "stock_available": "In stock",
    "star_rating": 3,
    "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "detail_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "upc": "a897fe39b1053632",
    "product_type": "Books",
    "price_excl_tax": "£51.77",
    "price_incl_tax": "£51.77",
    "tax": "£0.00",
    "availability": "In stock (22 available)",
    "number_of_reviews": "0",
    "description": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative poems have been beloved by generations of kids and adults. This is a book that families can read together for years to come.",
    "category": "Poetry"
}

# Expected data for book with special characters
EXPECTED_SPECIAL_CHARS_BOOK_DATA = {
    "title": "Book with Special & Characters: Quotes 'n' Stuff",
    "price": "£99.99",
    "stock_available": "In stock (1 available)",
    "star_rating": 3,
    "image_url": "https://books.toscrape.com/media/cache/special.jpg",
    "detail_url": "https://books.toscrape.com/catalogue/special-chars_1/index.html",
    "upc": "special123&chars",
    "product_type": "Books & Literature",
    "price_excl_tax": "£99.99",
    "price_incl_tax": "£99.99",
    "tax": "£0.00",
    "availability": "In stock (1 available)",
    "number_of_reviews": "5",
    "description": "This book contains special characters like & (ampersand), quotes 'single' and \"double\", and unicode characters: café, résumé, naïve. It's designed to test edge cases in text processing.",
    "category": "Fiction & Literature"
}

# Expected data for incomplete book (missing some fields)
EXPECTED_INCOMPLETE_BOOK_DATA = {
    "title": "Incomplete Book",
    "price": "£25.00",
    "stock_available": "",
    "star_rating": 2,
    "image_url": "",
    "detail_url": "https://books.toscrape.com/catalogue/incomplete-book_1/index.html",
    "upc": "incomplete123",
    "product_type": "Books",
    "price_excl_tax": "",
    "price_incl_tax": "",
    "tax": "",
    "availability": "",
    "number_of_reviews": "",
    "description": "",
    "category": ""
}

# Sample list of multiple books for testing
SAMPLE_BOOKS_LIST = [
    {
        "title": "Test Book 1",
        "price": "£19.99",
        "stock_available": "In stock",
        "star_rating": 4,
        "image_url": "https://example.com/image1.jpg",
        "detail_url": "https://example.com/book1",
        "upc": "test123",
        "product_type": "Books",
        "description": "A test book for unit testing."
    },
    {
        "title": "Test Book 2",
        "price": "£25.50",
        "stock_available": "Out of stock",
        "star_rating": 2,
        "image_url": "https://example.com/image2.jpg",
        "detail_url": "https://example.com/book2",
        "upc": "test456",
        "product_type": "Books",
        "description": "Another test book for unit testing."
    },
    {
        "title": "Test Book 3 with Very Long Title That Should Be Handled Properly by the JSON Serialization Process",
        "price": "£150.00",
        "stock_available": "In stock (1 available)",
        "star_rating": 5,
        "image_url": "https://example.com/very-long-image-url-that-tests-edge-cases.jpg",
        "detail_url": "https://example.com/very-long-book-url-for-testing",
        "upc": "verylongtest789",
        "product_type": "Books",
        "description": "A test book with a very long title and description to test edge cases in data processing and JSON serialization. This description contains multiple sentences and should be handled properly by all functions."
    }
]

# Star rating test cases
STAR_RATING_TEST_CASES = [
    ("star-rating One", 1),
    ("star-rating Two", 2),
    ("star-rating Three", 3),
    ("star-rating Four", 4),
    ("star-rating Five", 5),
    ("star-rating one", 1),  # lowercase
    ("star-rating FIVE", 5),  # uppercase
    ("star-rating Invalid", 0),  # invalid rating
    ("invalid-class", 0),  # invalid class format
    ("", 0),  # empty class
    ("star-rating", 0),  # missing rating word
    ("star-rating Six", 0),  # invalid rating word
    ("rating Three", 0),  # missing "star-" prefix
]

# URL generation test cases
URL_GENERATION_TEST_CASES = [
    ("https://books.toscrape.com/", 1, "https://books.toscrape.com/"),
    ("https://books.toscrape.com/", 2, "https://books.toscrape.com/catalogue/page-2.html"),
    ("https://books.toscrape.com/", 10, "https://books.toscrape.com/catalogue/page-10.html"),
    ("https://books.toscrape.com", 3, "https://books.toscrape.com/catalogue/page-3.html"),  # no trailing slash
    ("https://example.com/", 5, "https://example.com/catalogue/page-5.html"),
    ("http://localhost:8000/", 2, "http://localhost:8000/catalogue/page-2.html"),
]

# Pagination parsing test cases
PAGINATION_TEST_CASES = [
    ("Page 1 of 50", 50),
    ("Page 5 of 10", 10),
    ("Page 1 of 1", 1),
    ("Page 25 of 100", 100),
    ("Page X of Y", 1),  # malformed - should default to 1
    ("Invalid format", 1),  # invalid format - should default to 1
    ("", 1),  # empty - should default to 1
]

# Network error scenarios for testing
NETWORK_ERROR_SCENARIOS = [
    ("ConnectionError", "Network unreachable"),
    ("Timeout", "Request timeout"),
    ("HTTPError", "404 Not Found"),
    ("HTTPError", "500 Internal Server Error"),
    ("Exception", "Generic network error"),
]

# File operation error scenarios
FILE_ERROR_SCENARIOS = [
    ("PermissionError", "Access denied"),
    ("FileNotFoundError", "File not found"),
    ("OSError", "Disk full"),
    ("UnicodeEncodeError", "Encoding error"),
    ("JSONEncodeError", "Invalid JSON data"),
]

# CLI argument test cases
CLI_ARGUMENT_TEST_CASES = [
    ([], {"threads": 10, "pages": 1}),  # default values
    (["--threads", "5"], {"threads": 5, "pages": 1}),  # custom threads
    (["--pages", "3"], {"threads": 10, "pages": 3}),  # custom pages
    (["--threads", "20", "--pages", "5"], {"threads": 20, "pages": 5}),  # both custom
    (["--threads", "1", "--pages", "100"], {"threads": 1, "pages": 100}),  # edge values
]

# Edge case data for testing
EDGE_CASE_DATA = {
    "empty_book": {
        "title": "",
        "price": "",
        "stock_available": "",
        "star_rating": 0,
        "image_url": "",
        "detail_url": ""
    },
    "null_values": {
        "title": None,
        "price": None,
        "stock_available": None,
        "star_rating": None,
        "image_url": None,
        "detail_url": None
    },
    "very_long_strings": {
        "title": "A" * 1000,  # Very long title
        "price": "£" + "9" * 100 + ".99",  # Very long price
        "description": "Lorem ipsum " * 500,  # Very long description
    },
    "special_characters": {
        "title": "Book with 特殊字符 and émojis 📚",
        "description": "Contains unicode: café, résumé, naïve, and symbols: @#$%^&*()",
        "price": "£19.99",
    }
}

# Mock HTTP status codes for testing
HTTP_STATUS_CODES = [
    (200, "OK"),
    (404, "Not Found"),
    (500, "Internal Server Error"),
    (503, "Service Unavailable"),
    (403, "Forbidden"),
    (401, "Unauthorized"),
    (408, "Request Timeout"),
]

# Threading test scenarios
THREADING_TEST_SCENARIOS = [
    {"max_workers": 1, "books_count": 5},
    {"max_workers": 5, "books_count": 10},
    {"max_workers": 10, "books_count": 20},
    {"max_workers": 20, "books_count": 5},  # more workers than books
]