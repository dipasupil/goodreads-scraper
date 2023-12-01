import json

rating_star_map = {
    "it was amazing": 5,
    "really liked it": 4,
    "liked it": 3,
    "was ok": 2,
    "did not like it": 1,
}

def parse_data_from_list_section(book):
    isbn = book.css('td.field.isbn div.value::text').get().strip()
    isbn13 = book.css('td.field.isbn13 div.value::text').get().strip()
    amzn_asin = book.css('td.field.asin div.value::text').get().strip()
    title = book.css('td.field.title div.value a::text').get().strip()
    orig_pub_date = book.css('td.field.date_pub div.value::text').get().strip()
    edition_pub_date = book.css('td.field.date_pub_edition div.value::text').get().strip()
    avg_rating = book.css('td.field.avg_rating div.value::text').get().strip()
    num_ratings = book.css('td.field.num_ratings div.value::text').get().strip()
    user_rating_text = ""
    if book.css('td.field.rating div.value span span::text').get():
        user_rating_text = book.css('td.field.rating div.value span span::text').get().strip()


    return {
        "title": title or "",
        "isbn": isbn or "",
        "isbn13": isbn13 or "",
        "amzn_asin": amzn_asin or "",
        "orig_pub_date": orig_pub_date or "",
        "edition_pub_date": edition_pub_date or "",
        "avg_rating": avg_rating or "",
        "user_rating": rating_star_map.get(user_rating_text),
        "num_ratings": num_ratings or ""
    }

def parse_data_from_book_page(response):
    script = response.css('script[type="application/ld+json"]').get()
    book_data = json.loads(str(script).split("<script type=\"application/ld+json\">")[1].split("</script>")[0].strip())
    return {
            "num_reviews": book_data.get('aggregateRating', {}).get('reviewCount'),
            "rating_histogram": response.css('div.RatingsHistogram__labelTotal::text').getall(),
            "book_format": book_data.get('bookFormat'),
            "full_title": book_data.get('name'),
            "series": (response.css('a[aria-label]::text').get()) or "",
            "author(s)": [author for author in book_data.get('author', []) if author],
            "description": " ".join(response.css('div[data-testid="description"] *::text').getall()).strip(),
            "genres": response.xpath('//a[contains(@href, "https://www.goodreads.com/genres/")]/span/text()').getall(),
            "page_count": book_data.get('numberOfPages'),
            "language": book_data.get('inLanguage'),
            "awards": book_data.get('awards'), 
            "goodreads_url": response.url,
            "cover_img": book_data.get('image')
        }