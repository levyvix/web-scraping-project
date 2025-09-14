# Test Infrastructure Documentation

## Overview

This document describes the comprehensive test infrastructure that has been set up to achieve 100% test coverage for the web scraping project.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── fixtures/                   # Test data and mock responses
│   ├── __init__.py
│   ├── mock_responses.py       # Mock HTML responses for different scenarios
│   └── test_data.py           # Expected data structures and test cases
└── test_main/                 # Main test directory
    ├── __init__.py
    └── test_main.py           # Existing tests (to be enhanced)
```

## Fixtures Available

### Shared Fixtures (conftest.py)

#### File Operations
- `temp_dir`: Temporary directory for file operations
- `temp_json_file`: Temporary JSON file path
- `mock_file_operations`: Mock file I/O operations

#### Network Operations
- `mock_network_requests`: Mock HTTP requests
- `mock_scrapling_adaptor`: Mock Scrapling Adaptor object
- `mock_fetcher_response`: Mock Fetcher response

#### Threading
- `mock_threading`: Mock ThreadPoolExecutor operations

#### Test Data
- `expected_book_data`: Expected basic book data structure
- `expected_detailed_book_data`: Expected detailed book data after processing
- `expected_special_chars_book_data`: Expected data with special characters
- `sample_books_list`: List of sample books for testing

#### Test Cases
- `star_rating_test_cases`: Test cases for star rating extraction
- `url_generation_test_cases`: Test cases for URL generation
- `pagination_test_cases`: Test cases for pagination parsing
- `cli_test_cases`: Test cases for CLI argument parsing
- `edge_case_data`: Edge case data for boundary testing
- `http_status_codes`: HTTP status codes for error testing
- `threading_test_scenarios`: Threading scenarios for concurrent testing

#### Mock HTML Responses
- `mock_book_listing_page`: Valid book listing page
- `mock_book_detail_page`: Complete book detail page
- `mock_empty_page`: Empty page with no books
- `mock_malformed_page`: Malformed page with missing elements
- `mock_single_page`: Single page without pagination
- `mock_incomplete_detail_page`: Detail page with missing elements
- `mock_malformed_detail_page`: Detail page with malformed table
- `mock_pagination_page`: Page 2 of 10 with pagination
- `mock_no_pagination_page`: Page without pagination info
- `mock_malformed_pagination_page`: Page with malformed pagination
- `mock_special_chars_page`: Page with special characters
- `mock_special_chars_detail_page`: Detail page with special characters

## Mock Data Categories

### HTML Response Scenarios
1. **Valid Pages**: Complete, well-formed HTML with all expected elements
2. **Empty Pages**: Pages with no books or content
3. **Malformed Pages**: Pages with missing or incorrectly structured elements
4. **Special Characters**: Pages with unicode, special characters, and edge cases
5. **Pagination Variants**: Different pagination states and formats

### Test Data Types
1. **Expected Results**: Known good data structures for comparison
2. **Edge Cases**: Boundary conditions, empty values, very long strings
3. **Error Scenarios**: Network errors, file errors, parsing errors
4. **Configuration Cases**: Different CLI arguments and threading scenarios

## Configuration

### pytest.ini
- Configured for 100% coverage requirement
- Organized test markers for different test categories
- HTML coverage reports generated in `htmlcov/`
- Strict configuration for reliable test execution

### Test Markers
- `unit`: Unit tests for individual functions
- `integration`: Integration tests for component interactions
- `error_handling`: Tests for error scenarios and exception handling
- `edge_cases`: Tests for boundary conditions and edge cases
- `cli`: Tests for command-line interface
- `network`: Tests involving network operations (mocked)
- `file_ops`: Tests involving file operations
- `threading`: Tests for concurrent processing
- `slow`: Tests that take longer to run

## Usage Examples

### Using Fixtures in Tests
```python
def test_save_to_json(temp_dir, sample_books_list):
    """Test saving books to JSON file."""
    output_file = temp_dir / "test_books.json"
    save_to_json(sample_books_list, str(output_file))
    assert output_file.exists()

def test_star_rating_extraction(star_rating_test_cases, mock_scrapling_adaptor):
    """Test all star rating scenarios."""
    for class_string, expected_rating in star_rating_test_cases:
        mock_scrapling_adaptor.find.return_value.attrib = {"class": class_string}
        result = extract_star_rating(mock_scrapling_adaptor)
        assert result == expected_rating
```

### Running Tests
```bash
# Run all tests with coverage
uv run pytest

# Run specific test categories
uv run pytest -m unit
uv run pytest -m error_handling

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov-report=html
```

## Next Steps

This infrastructure provides the foundation for implementing comprehensive tests to achieve 100% coverage. The next tasks will use these fixtures to create:

1. Enhanced unit tests for all functions
2. Error handling and exception tests
3. Integration tests for component interactions
4. CLI and main function tests
5. Edge case and boundary condition tests

All tests will use the mock data and fixtures provided here to ensure fast, reliable, and deterministic test execution without external dependencies.
