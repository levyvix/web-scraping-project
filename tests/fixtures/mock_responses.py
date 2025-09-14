"""
Mock HTML responses for different test scenarios.
"""

# Mock response for book detail page with missing elements
MOCK_INCOMPLETE_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Incomplete Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <ul class="breadcrumb">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                <li class="active">Incomplete Book</li>
            </ul>
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>Incomplete Book</h1>
                    <p class="star-rating Two">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£25.00</p>
                    <table class="table table-striped">
                        <tr>
                            <th>UPC</th>
                            <td>incomplete123</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <td>Books</td>
                        </tr>
                        <!-- Missing other product info -->
                    </table>
                </div>
            </div>
            <!-- Missing product description -->
        </div>
    </div>
</body>
</html>
"""

# Mock response for book detail page with malformed table
MOCK_MALFORMED_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Malformed Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>Malformed Book</h1>
                    <table class="table table-striped">
                        <tr>
                            <!-- Missing th element -->
                            <td>malformed123</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <!-- Missing td element -->
                        </tr>
                        <!-- Malformed row -->
                        <tr>
                            <th>Price</th>
                            <td>£30.00</td>
                            <td>Extra cell</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Mock response for pagination with different page numbers
MOCK_PAGINATION_PAGE_2_OF_10 = """
<!DOCTYPE html>
<html>
<head><title>Page 2 | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <section>
                <div class="row">
                    <aside class="sidebar col-sm-4 col-md-3">
                        <ul class="pager">
                            <li class="previous"><a href="catalogue/page-1.html">previous</a></li>
                            <li class="current">
                                Page 2 of 10
                            </li>
                            <li class="next"><a href="catalogue/page-3.html">next</a></li>
                        </ul>
                    </aside>
                    <div class="col-sm-8 col-md-9">
                        <section>
                            <ol class="row">
                                <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                    <article class="product_pod">
                                        <div class="image_container">
                                            <a href="catalogue/page2-book_1/index.html">
                                                <img src="media/cache/page2.jpg" alt="Page 2 Book" class="thumbnail">
                                            </a>
                                        </div>
                                        <p class="star-rating Four">
                                            <i class="icon-star"></i>
                                        </p>
                                        <h3><a href="catalogue/page2-book_1/index.html" title="Page 2 Book">Page 2 Book</a></h3>
                                        <div class="product_price">
                                            <p class="price_color">£15.99</p>
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

# Mock response for page with no pagination (malformed)
MOCK_NO_PAGINATION_INFO = """
<!DOCTYPE html>
<html>
<head><title>No Pagination | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <section>
                <div class="row">
                    <aside class="sidebar col-sm-4 col-md-3">
                        <!-- No pager element -->
                    </aside>
                    <div class="col-sm-8 col-md-9">
                        <section>
                            <ol class="row">
                                <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                    <article class="product_pod">
                                        <div class="image_container">
                                            <a href="catalogue/no-pagination-book_1/index.html">
                                                <img src="media/cache/nopag.jpg" alt="No Pagination Book" class="thumbnail">
                                            </a>
                                        </div>
                                        <p class="star-rating One">
                                            <i class="icon-star"></i>
                                        </p>
                                        <h3><a href="catalogue/no-pagination-book_1/index.html" title="No Pagination Book">No Pagination Book</a></h3>
                                        <div class="product_price">
                                            <p class="price_color">£8.99</p>
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

# Mock response for page with malformed pagination
MOCK_MALFORMED_PAGINATION = """
<!DOCTYPE html>
<html>
<head><title>Malformed Pagination | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <section>
                <div class="row">
                    <aside class="sidebar col-sm-4 col-md-3">
                        <ul class="pager">
                            <li class="current">
                                Page X of Y
                            </li>
                        </ul>
                    </aside>
                    <div class="col-sm-8 col-md-9">
                        <section>
                            <ol class="row">
                                <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                    <article class="product_pod">
                                        <div class="image_container">
                                            <a href="catalogue/malformed-pagination-book_1/index.html">
                                                <img src="media/cache/malform.jpg" alt="Malformed Pagination Book" class="thumbnail">
                                            </a>
                                        </div>
                                        <p class="star-rating Two">
                                            <i class="icon-star"></i>
                                        </p>
                                        <h3><a href="catalogue/malformed-pagination-book_1/index.html" title="Malformed Pagination Book">Malformed Pagination Book</a></h3>
                                        <div class="product_price">
                                            <p class="price_color">£12.50</p>
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

# Mock response with special characters and edge cases
MOCK_SPECIAL_CHARACTERS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Special Characters | Books to Scrape</title></head>
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
                                            <a href="catalogue/special-chars_1/index.html">
                                                <img src="media/cache/special.jpg" alt="Special & Characters" class="thumbnail">
                                            </a>
                                        </div>
                                        <p class="star-rating Three">
                                            <i class="icon-star"></i>
                                        </p>
                                        <h3><a href="catalogue/special-chars_1/index.html" title="Book with Special & Characters: Quotes 'n' Stuff">Book with Special & Characters: Quotes 'n' Stuff</a></h3>
                                        <div class="product_price">
                                            <p class="price_color">£99.99</p>
                                        </div>
                                        <p class="instock availability">
                                            <i class="icon-ok"></i>
                                            In stock (1 available)
                                        </p>
                                    </article>
                                </li>
                                <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                                    <article class="product_pod">
                                        <div class="image_container">
                                            <a href="catalogue/unicode-book_2/index.html">
                                                <img src="media/cache/unicode.jpg" alt="Unicode Book" class="thumbnail">
                                            </a>
                                        </div>
                                        <p class="star-rating Five">
                                            <i class="icon-star"></i>
                                        </p>
                                        <h3><a href="catalogue/unicode-book_2/index.html" title="Café & Résumé: A Story of Naïve Dreams">Café & Résumé: A Story of Naïve Dreams</a></h3>
                                        <div class="product_price">
                                            <p class="price_color">£45.67</p>
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

# Mock response for book detail with special characters
MOCK_SPECIAL_CHARS_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Special & Characters | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <ul class="breadcrumb">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                <li><a href="../catalogue/category/books/fiction_10/index.html">Fiction & Literature</a></li>
                <li class="active">Special & Characters</li>
            </ul>
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>Book with Special & Characters: Quotes 'n' Stuff</h1>
                    <p class="star-rating Three">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£99.99</p>
                    <table class="table table-striped">
                        <tr>
                            <th>UPC</th>
                            <td>special123&chars</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <td>Books & Literature</td>
                        </tr>
                        <tr>
                            <th>Price (excl. tax)</th>
                            <td>£99.99</td>
                        </tr>
                        <tr>
                            <th>Price (incl. tax)</th>
                            <td>£99.99</td>
                        </tr>
                        <tr>
                            <th>Tax</th>
                            <td>£0.00</td>
                        </tr>
                        <tr>
                            <th>Availability</th>
                            <td>In stock (1 available)</td>
                        </tr>
                        <tr>
                            <th>Number of reviews</th>
                            <td>5</td>
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
            <p>This book contains special characters like & (ampersand), quotes 'single' and "double", and unicode characters: café, résumé, naïve. It's designed to test edge cases in text processing.</p>
        </div>
    </div>
</body>
</html>
"""

# Mock response for complete book detail page with all fields present
MOCK_COMPLETE_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Complete Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <ul class="breadcrumb">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                <li><a href="../catalogue/category/books/mystery_3/index.html">Mystery</a></li>
                <li class="active">Complete Book</li>
            </ul>
            <div class="row">
                <div class="col-sm-6">
                    <div id="product_gallery">
                        <div id="product_gallery_carousel">
                            <img id="product_image" src="../../media/cache/complete.jpg" alt="Complete Book">
                        </div>
                    </div>
                </div>
                <div class="col-sm-6 product_main">
                    <h1>Complete Book</h1>
                    <p class="star-rating Four">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£35.99</p>
                    <p class="instock availability">
                        <i class="icon-ok"></i>
                        In stock (15 available)
                    </p>
                    <table class="table table-striped">
                        <tr>
                            <th>UPC</th>
                            <td>complete123456789</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <td>Books</td>
                        </tr>
                        <tr>
                            <th>Price (excl. tax)</th>
                            <td>£35.99</td>
                        </tr>
                        <tr>
                            <th>Price (incl. tax)</th>
                            <td>£35.99</td>
                        </tr>
                        <tr>
                            <th>Tax</th>
                            <td>£0.00</td>
                        </tr>
                        <tr>
                            <th>Availability</th>
                            <td>In stock (15 available)</td>
                        </tr>
                        <tr>
                            <th>Number of reviews</th>
                            <td>12</td>
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
            <p>This is a complete book with all fields present. It has a comprehensive description that includes multiple sentences and provides detailed information about the book's content, themes, and target audience. This description is used to test the complete processing of book detail pages.</p>
        </div>
    </div>
</body>
</html>
"""

# Mock response for book detail page with missing description
MOCK_NO_DESCRIPTION_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>No Description Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <ul class="breadcrumb">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                <li><a href="../catalogue/category/books/romance_8/index.html">Romance</a></li>
                <li class="active">No Description Book</li>
            </ul>
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>No Description Book</h1>
                    <p class="star-rating Two">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£18.50</p>
                    <table class="table table-striped">
                        <tr>
                            <th>UPC</th>
                            <td>nodesc123</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <td>Books</td>
                        </tr>
                        <tr>
                            <th>Price (excl. tax)</th>
                            <td>£18.50</td>
                        </tr>
                        <tr>
                            <th>Price (incl. tax)</th>
                            <td>£18.50</td>
                        </tr>
                        <tr>
                            <th>Tax</th>
                            <td>£0.00</td>
                        </tr>
                        <tr>
                            <th>Availability</th>
                            <td>In stock (8 available)</td>
                        </tr>
                        <tr>
                            <th>Number of reviews</th>
                            <td>3</td>
                        </tr>
                    </table>
                </div>
            </div>
            <!-- Missing product description section entirely -->
        </div>
    </div>
</body>
</html>
"""

# Mock response for book detail page with missing category (no breadcrumb)
MOCK_NO_CATEGORY_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>No Category Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <!-- Missing breadcrumb navigation -->
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>No Category Book</h1>
                    <p class="star-rating Five">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£42.00</p>
                    <table class="table table-striped">
                        <tr>
                            <th>UPC</th>
                            <td>nocat456</td>
                        </tr>
                        <tr>
                            <th>Product Type</th>
                            <td>Books</td>
                        </tr>
                        <tr>
                            <th>Price (excl. tax)</th>
                            <td>£42.00</td>
                        </tr>
                        <tr>
                            <th>Price (incl. tax)</th>
                            <td>£42.00</td>
                        </tr>
                        <tr>
                            <th>Tax</th>
                            <td>£0.00</td>
                        </tr>
                        <tr>
                            <th>Availability</th>
                            <td>In stock (5 available)</td>
                        </tr>
                        <tr>
                            <th>Number of reviews</th>
                            <td>7</td>
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
            <p>This book has no category information because the breadcrumb navigation is missing.</p>
        </div>
    </div>
</body>
</html>
"""

# Mock response for book detail page with malformed product info table
MOCK_MALFORMED_TABLE_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Malformed Table Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <ul class="breadcrumb">
                <li><a href="../index.html">Home</a></li>
                <li><a href="../catalogue/category/books_1/index.html">Books</a></li>
                <li><a href="../catalogue/category/books/science_22/index.html">Science</a></li>
                <li class="active">Malformed Table Book</li>
            </ul>
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>Malformed Table Book</h1>
                    <p class="star-rating One">
                        <i class="icon-star"></i>
                    </p>
                    <p class="price_color">£28.75</p>
                    <table class="table table-striped">
                        <!-- Row with missing th -->
                        <tr>
                            <td>malformed789</td>
                        </tr>
                        <!-- Row with missing td -->
                        <tr>
                            <th>Product Type</th>
                        </tr>
                        <!-- Normal row -->
                        <tr>
                            <th>Price (excl. tax)</th>
                            <td>£28.75</td>
                        </tr>
                        <!-- Row with extra cells -->
                        <tr>
                            <th>Price (incl. tax)</th>
                            <td>£28.75</td>
                            <td>Extra cell</td>
                        </tr>
                        <!-- Row with empty cells -->
                        <tr>
                            <th></th>
                            <td></td>
                        </tr>
                        <!-- Row with only whitespace -->
                        <tr>
                            <th>   </th>
                            <td>   </td>
                        </tr>
                        <!-- Valid row at the end -->
                        <tr>
                            <th>Number of reviews</th>
                            <td>2</td>
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
            <p>This book has a malformed product information table with missing and extra elements.</p>
        </div>
    </div>
</body>
</html>
"""

# Mock response for book detail page with empty/minimal content
MOCK_MINIMAL_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Minimal Book | Books to Scrape</title></head>
<body>
    <div class="container-fluid page">
        <div class="page_inner">
            <div class="row">
                <div class="col-sm-6 product_main">
                    <h1>Minimal Book</h1>
                    <!-- No star rating -->
                    <!-- No price -->
                    <!-- No product table -->
                </div>
            </div>
            <!-- No description -->
        </div>
    </div>
</body>
</html>
"""
