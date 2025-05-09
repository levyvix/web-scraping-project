from scrapling.fetchers import Fetcher
from loguru import logger
from tqdm import tqdm


def save_to_json(data: dict) -> None:
    import json

    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main() -> None:
    logger.info("Fetching page...")
    page = Fetcher.get("https://books.toscrape.com/", stealthy_headers=True)

    if page.status != 200:
        logger.error(f"Failed to fetch page. Status code: {page.status}")
        return

    logger.info("Parsing page...")
    books = page.find_all("li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"})

    logger.info(f"Found {len(books)} books")
    if not books:
        logger.error("No books found!")
        return

    logger.info("Extracting data...")
    books = list(
        tqdm(
            map(
                lambda b: {
                    "title": b.find("h3 > a").attrib["title"],
                    "price": b.find("div.product_price").find("p.price_color").text,
                    "stock_available": "".join(
                        b.css(
                            "p.instock.availability::text",
                        ).get_all()
                    ).strip(),
                },
                books,
            ),
            desc="Extracting data",
            total=len(books),
        )
    )

    logger.info("Saving to JSON...")

    save_to_json(books)

    logger.success("Done!")


if __name__ == "__main__":
    main()
