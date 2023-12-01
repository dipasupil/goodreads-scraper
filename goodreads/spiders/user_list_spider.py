import scrapy
import time
from goodreads.parse_functions import parse_data_from_list_section, parse_data_from_book_page

class UserListSpider(scrapy.Spider):
    name = "list"
    allowed_domains = ["goodreads.com"]
    cookies = {"start_expanded_book_details": "true"}
    num_pages_default = 100
    
    def __init__(self, start_urls=None, *args, **kwargs):
        super(UserListSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_urls] or [str(kwargs.get('start_urls'))]

    # goes through user list page by page, parsing data from each book on each page
    def parse(self, response):
        
        # parses some data from the list section, then parses from book's main page. Yield combined results.
        for book in response.css('tr.bookalike.review'):
            book_data_from_list = parse_data_from_list_section(book)
            book_url_suffix = str(book.css('td.title div a[href]::attr(href)').get())
            book_url_full = f"https://www.goodreads.com{book_url_suffix}"
            time.sleep(1)
            yield response.follow(url=book_url_full, callback=self.parse_book, meta={'book_data_from_list': book_data_from_list})
                
        # parse next page on list, if one exists.
        next_page = response.css('a.next_page::attr(href)').get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)
        
    # parses individual book pages
    def parse_book(self, response):
        
        book_data_from_list = response.meta.get('book_data_from_list', {})
        page_loaded = response.css('script[type="application/ld+json"]').get()
        
        # if page was loaded properly, parse the book data. If not, try again.
        if page_loaded:
            book_data_from_page = parse_data_from_book_page(response)
            book_data_from_list.update(book_data_from_page)
            yield book_data_from_list
        else:
            time.sleep(2)
            yield scrapy.Request(url=response.url, callback=self.parse_book, dont_filter=True, meta=response.meta)
    