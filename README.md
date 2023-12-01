# goodreads-scraper
Scrapy spider that scrapes data from Goodreads users' book lists and outputs cleaned data about the books on the list to .CSV and .JSON formats.

# How to run
Run <code>python crawl.py -- list_url 'https://www.goodreads.com/review/list/139794858-alex?shelf=read'</code>

Replace the passed in URL with any goodreads bookshelf that you'd like to crawl.

This will create an <code>outputs</code> folder in the high level directory. CSV and JSON outputs will be stored in subfolders. 
