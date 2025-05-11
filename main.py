from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptors, Adaptor
from loguru import logger
from tqdm import tqdm
import concurrent.futures


def save_to_json(data: dict) -> None:
    """Save the extracted data to a JSON file.
    
    Args:
        data (dict): The data to save.
    
    """
    import json

    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def process_book(book: Adaptor) -> dict[str, str]:
    """Process a single book and extract its data."""
    return {
        "title": book.find("h3 > a").attrib["title"],
        "price": book.find("div.product_price").find("p.price_color").text,
        "stock_available": "".join(
            book.css(
                "p.instock.availability::text",
            ).get_all()
        ).strip(),
    }


def main(max_workers: int = 10) -> None:
    logger.info("Fetching page...")
    page = Fetcher.get("https://books.toscrape.com/", stealthy_headers=True)

    if page.status != 200:
        logger.error(f"Failed to fetch page. Status code: {page.status}")
        return

    logger.info("Parsing page...")
    books: Adaptors = page.find_all("li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"})

    logger.info(f"Found {len(books)} books")
    if not books:
        logger.error("No books found!")
        return

    logger.info("Extracting data with multithreading...")
    
    # Process books in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list of futures
        futures = [executor.submit(process_book, book) for book in books]
        
        # Process results as they complete
        processed_books = []
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            desc="Extracting data",
            total=len(books),
        ):
            processed_books.append(future.result())
    
    books = processed_books

    logger.info("Saving to JSON...")

    save_to_json(books)

    logger.success("Done!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web scraper with multithreading")
    parser.add_argument(
        "--threads", 
        type=int, 
        default=10, 
        help="Number of worker threads (default: 10)"
    )
    
    args = parser.parse_args()
    main(max_workers=args.threads)
