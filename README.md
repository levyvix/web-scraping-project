# Web Scraping Project with Scrapling

A modern web scraping project that demonstrates how to extract book information from [Books to Scrape](https://books.toscrape.com/) using the Scrapling library.

## 🚀 Technologies

- **Python 3.10+** - The core programming language
- **[Scrapling](https://github.com/levy-victor/scrapling)** - A modern, fast, and flexible web scraping library
- **UV** - A fast Python package installer and resolver
- **Loguru** - For beautiful and easy logging
- **tqdm** - For progress bars

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/web-scraping-project.git
   cd web-scraping-project
   ```

2. **Install dependencies using UV**
   ```bash
   # Install UV if you haven't already
   pip install uv
   
   # Sync dependencies
   uv sync
   ```

   This will install all the required dependencies in a virtual environment.

## 🛠️ Project Structure

```
.
├── main.py           # Main script containing the web scraping logic
├── books.json        # Output file with scraped book data
├── pyproject.toml    # Project dependencies and metadata
└── README.md         # This file
```

## 🚀 Usage

### Basic Usage

Run the scraper with default settings (single page, 10 worker threads):

```bash
python main.py
```

### Advanced Options

The script supports the following command-line arguments:

- `--threads`: Number of worker threads to use for concurrent scraping (default: 10)
  ```bash
  python main.py --threads 20
  ```

- `--pages`: Maximum number of pages to scrape (default: 1)
  ```bash
  python main.py --pages 5
  ```

### Examples

1. Scrape 3 pages using 15 worker threads:
   ```bash
   python main.py --threads 15 --pages 3
   ```

2. Scrape just the first page with default settings:
   ```bash
   python main.py
   ```

3. View help message:
   ```bash
   python main.py --help
   ```

### Output

The scraped data will be saved to `books.json` in the project root directory. The file will contain an array of book objects, each with the following structure:

```json
{
  "title": "Book Title",
  "price": "£10.00",
  "stock_available": "In stock"
}
```

## 🔍 About Scrapling

This project uses [Scrapling](https://github.com/levy-victor/scrapling), a modern web scraping library that provides:

- Simple and intuitive API
- Built-in support for modern web technologies
- Async/await support
- Built-in rate limiting and retries
- Support for both CSS and XPath selectors

## 📊 Data Flow

```mermaid
flowchart TD
    A[Start] --> B[Fetch books.toscrape.com]
    B --> C{Status 200?}
    C -->|Yes| D[Find all book elements]
    C -->|No| E[Log error]
    D --> F[Extract book data]
    F --> G[Save to JSON]
    G --> H[Done]
    E --> H
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
