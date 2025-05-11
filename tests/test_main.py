from main import get_page_url


def test_get_page_url():
    # Test with a valid URL
    url = "https://example.com"
    expected_output = "https://example.com/catalogue/page-2.html"
    assert get_page_url(url, 2) == expected_output

    # Test with a different page number
    expected_output = "https://example.com/catalogue/page-3.html"
    assert get_page_url(url, 3) == expected_output
