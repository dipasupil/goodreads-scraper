import argparse
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from goodreads.spiders.user_list_spider import UserListSpider
from data_cleaning import *


def run_spider(list_url):
    settings = get_project_settings()    
    process = CrawlerProcess(settings)
    process.crawl(UserListSpider, start_urls=list_url)
    process.start()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process list URL and number of pages.")
    parser.add_argument("--list_url", type=str, help="URL of the list")
    args = parser.parse_args()
    
    # create output directory for where all list data will go
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    
    
    # start spider, and then clean crawled data
    run_spider(list_url=args.list_url)
    clean_and_dump_data(list_url=args.list_url)
