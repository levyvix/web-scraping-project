from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptors, Adaptor
from utils.logger import logger
from tqdm import tqdm
import concurrent.futures
import re
from typing import Dict, List, Any
from urllib.parse import urljoin


def save_to_json(data: List[Dict[str, Any]], filename: str = "books.json") -> None:
    """Save the extracted data to a JSON file.

    Args:
        data (List[Dict[str, Any]]): The data to save.
        filename (str, optional): The name of the output file. Defaults to "books.json".
    """
    import json

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def extract_star_rating(book: Adaptor) -> int:
    """Extract the star rating from a book element.

    Args:
        book (Adaptor): The book element.

    Returns:
        int: The star rating (1-5).
    """
    star_class = book.find("p.star-rating")
    if not star_class:
        logger.warning("No star rating found for book.")
        return 0

    star_class = star_class.attrib.get("class", "")

    rating_match = re.search(r"star-rating ([A-Za-z]+)", str(star_class))
    if not rating_match:
        return 0

    rating_text = rating_match.group(1).lower()
    rating_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

    return rating_map.get(rating_text, 0)


def process_book_listing(book: Adaptor, base_url: str) -> Dict[str, Any]:
    """Process a book from the listing page and extract basic data.

    Args:
        book (Adaptor): The book element.
        base_url (str): The base URL of the website.

    Returns:
        Dict[str, Any]: The extracted book data.
    """
    # Extract the book URL for detailed page scraping
    book_url_element = book.find("h3 > a")
    if not book_url_element:
        logger.warning("No book URL found in listing.")
        return {}

    relative_url = book_url_element.attrib.get("href", "")
    if "catalogue" not in str(relative_url):
        relative_url = f"catalogue/{relative_url}"
    book_url = urljoin(base_url, relative_url)

    # Extract data from the listing
    # title
    title = book_url_element.attrib.get("title", "")

    # price
    product_price = book.find("div.product_price > p.price_color")
    price = product_price.text if product_price else ""

    # stock available
    stock = "".join(
        book.css(
            "p.instock.availability::text",
        )
    ).strip()

    # image url
    image_url = book.find("div.image_container img")
    if image_url:
        image_url = image_url.attrib.get("src", "")
        # Convert relative URL to absolute URL
        image_url = urljoin(base_url, image_url)
    else:
        logger.warning("No image URL found for book.")
        image_url = ""

    return {
        "title": title,
        "price": price,
        "stock_available": stock,
        "star_rating": extract_star_rating(book),
        "image_url": image_url,
        "detail_url": book_url,
    }


def process_book_details(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch and process the book detail page to extract additional information.

    Args:
        book_data (Dict[str, Any]): The basic book data from the listing.

    Returns:
        Dict[str, Any]: The enhanced book data with details.
    """
    detail_url = book_data.get("detail_url")
    if not detail_url:
        logger.warning(f"No detail URL for book: {book_data.get('title')}")
        return book_data

    try:
        # Fetch the detail page
        logger.debug(f"Fetching details for: {book_data.get('title')}")
        detail_page = Fetcher.get(detail_url, stealthy_headers=True)

        if detail_page.status != 200:
            logger.warning(
                f"Failed to fetch detail page for {book_data.get('title')}. Status: {detail_page.status}"
            )
            return book_data

        # Extract product information table
        product_info = {}
        table_rows = detail_page.find_all("table.table-striped tr")

        for row in table_rows:
            header = "".join(row.css("th::text")).strip()
            value = "".join(row.css("td::text")).strip()
            product_info[header] = value

        # Extract description
        description_elem = detail_page.find("div#product_description + p")
        description = description_elem.text.strip() if description_elem else ""

        # Extract category
        breadcrumb = detail_page.find("ul.breadcrumb")
        category = (
            "".join(breadcrumb.find_all("li")[2].css("a::text")).strip()
            if breadcrumb
            else ""
        )

        # Update book data with details
        book_data.update(
            {
                "upc": product_info.get("UPC", ""),
                "product_type": product_info.get("Product Type", ""),
                "price_excl_tax": product_info.get("Price (excl. tax)", ""),
                "price_incl_tax": product_info.get("Price (incl. tax)", ""),
                "tax": product_info.get("Tax", ""),
                "availability": product_info.get("Availability", ""),
                "number_of_reviews": product_info.get("Number of reviews", ""),
                "description": description,
                "category": category,
            }
        )

        return book_data

    except Exception as e:
        logger.error(
            f"Error processing detail page for {book_data.get('title')}: {str(e)}"
        )
        return book_data


def get_total_pages(page: Adaptor, base_url: str) -> int:
    """Extract the total number of pages from the pagination.

    Args:
        page (Adaptor): The page adaptor.
        base_url (str): The base URL of the website.

    Returns:
        int: The total number of pages.
    """
    # Try to find the pagination element
    pager = page.find("ul.pager")
    if not pager:
        return 1

    # Look for the "next" button to determine if we're on the last page
    current_page = pager.find("li.current")
    if current_page:
        page_text = current_page.text.strip()
        match = re.search(r"Page (\d+) of (\d+)", page_text)
        if match:
            return int(match.group(2))

    # If we can't determine the total pages, default to 1
    return 1


def get_page_url(base_url: str, page_num: int) -> str:
    """Generate the URL for a specific page.

    Args:
        base_url (str): The base URL of the website.
        page_num (int): The page number.

    Returns:
        str: The URL for the specified page.
    """
    if page_num == 1:
        return base_url

    # The URL pattern for pages on books.toscrape.com is /catalogue/page-{page_num}.html
    return urljoin(base_url, f"catalogue/page-{page_num}.html")


def main(max_workers: int = 10, max_pages: int = 1) -> None:
    """Main function to scrape books from the website.

    Args:
        max_workers (int, optional): Maximum number of worker threads. Defaults to 10.
        max_pages (int, optional): Maximum number of pages to scrape. Defaults to 1.
    """
    base_url = "https://books.toscrape.com/"

    logger.info("Starting the scraping process...")

    # Fetch the first page to determine total pages
    logger.info("Fetching first page...")
    first_page = Fetcher.get(base_url, stealthy_headers=True)

    if first_page.status != 200:
        logger.error(f"Failed to fetch first page. Status code: {first_page.status}")
        raise Exception("Failed to fetch first page")

    # Determine total number of pages
    total_pages = get_total_pages(first_page, base_url)
    logger.info(f"Found {total_pages} pages of books")

    # Limit pages if max_pages is specified
    if max_pages and total_pages > max_pages:
        total_pages = max_pages
        logger.info(f"Limiting to {max_pages} pages as specified")

    all_books = []

    # Process each page
    for page_num in range(1, total_pages + 1):
        page_url = get_page_url(base_url, page_num)
        logger.info(f"Processing page {page_num}/{total_pages}: {page_url}")

        # Fetch the page
        if page_num == 1:
            page = first_page  # Reuse the first page we already fetched
        else:
            page = Fetcher.get(page_url, stealthy_headers=True)

            if page.status != 200:
                logger.error(
                    f"Failed to fetch page {page_num}. Status code: {page.status}"
                )
                continue

        # Extract books from the page
        books: Adaptors = page.find_all(
            "li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"}
        )

        logger.info(f"Found {len(books)} books on page {page_num}")
        if not books:
            logger.warning(f"No books found on page {page_num}!")
            continue

        # Process book listings in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a list of futures for processing book listings
            listing_futures = [
                executor.submit(process_book_listing, book, base_url) for book in books
            ]

            # Process results as they complete
            page_books: list[Dict[str, Any]] = []
            for future in tqdm(
                concurrent.futures.as_completed(listing_futures),
                desc=f"Extracting listings from page {page_num}",
                total=len(books),
            ):
                result = future.result()
                if result:
                    page_books.append(result)

        # Process book details in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a list of futures for processing book details
            detail_futures = [
                executor.submit(process_book_details, book_data)
                for book_data in page_books
            ]

            # Process results as they complete
            processed_books = []
            for future in tqdm(
                concurrent.futures.as_completed(detail_futures),
                desc=f"Fetching details for page {page_num} books",
                total=len(page_books),
            ):
                processed_books.append(future.result())

        # Add books from this page to the overall collection
        all_books.extend(processed_books)

        logger.success(f"Completed processing page {page_num}")

    logger.info(f"Total books collected: {len(all_books)}")

    # Save all books to JSON
    logger.info("Saving to JSON...")
    save_to_json(all_books)

    logger.success("Done!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Web scraper with multithreading and pagination"
    )
    parser.add_argument(
        "--threads", type=int, default=10, help="Number of worker threads (default: 10)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Maximum number of pages to scrape (default: 1)",
    )

    args = parser.parse_args()
    main(max_workers=args.threads, max_pages=args.pages)
