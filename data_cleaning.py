import os
import json
import codecs
import pandas as pd
import html
from datetime import datetime


# detects the format of the date string for standardization
def detect_date_format(date_str):
    formats = ["%b %d, %Y", "%b %Y", "%Y"]
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return fmt
        except ValueError:
            pass
    return None


# cleans up some of the full_titles
def clean_titles(book):
    book['full_title'] = html.unescape(book['full_title'])
    
    
# standardize all dates to y-m-d format. 
def clean_dates(book):
    
    orig_pub_date_str = book['orig_pub_date']
    edition_pub_date_str = book['edition_pub_date']
    orig_pub_date_fmt = detect_date_format(orig_pub_date_str)
    edition_pub_date_fmt = detect_date_format(edition_pub_date_str)
    
    if orig_pub_date_fmt is not None:
        date_obj = datetime.strptime(orig_pub_date_str, orig_pub_date_fmt)
        book['orig_pub_date'] = date_obj.strftime("%Y-%m-%d")
    else:
        book['orig_pub_date'] = ""
    
    if edition_pub_date_fmt is not None:
        date_obj = datetime.strptime(edition_pub_date_str, edition_pub_date_fmt)
        book['edition_pub_date'] = date_obj.strftime("%Y-%m-%d")
    else:
        book['edition_pub_date'] = ""
 
    
# removes the "@type" field, returns field as a dictionary instead of string
def clean_authors(book):
    for author in book['author(s)']:
        author.pop('@type')
    
    
# cleans histogram such that it returns a dictionary of star rating to number of ratings
def clean_histogram(book):
    
    cleaned_histogram = {}
    total_ratings = book['num_ratings']
    if total_ratings == 0:
        book['rating_histogram'] = {}
        return
    
    for i, rating in enumerate(book['rating_histogram']):
        star_rating = 5 - i
        num_ratings = int(rating.split("(")[0].strip().replace(",", ""))
        ratio = num_ratings / total_ratings
        cleaned_histogram[star_rating] = {
                                            "num_ratings": total_ratings,
                                            "ratio": ratio
                                         }
    
    book['rating_histogram'] = cleaned_histogram            


# cleans the number of reviews/ratings fields
def clean_ratings_and_reviews(book):
    if book['avg_rating']:
            book['avg_rating'] = float(book['avg_rating'].replace(",", ""))
        
    if book['num_ratings']:
        book['num_ratings'] = int(book['num_ratings'].replace(",", ""))

    return book


# creates directory for specific list's data to be dumped to
def create_output_directory(directory):
    output_dir = os.path.join('outputs', directory)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


# cleans all the data and dumps it all to an output folder
def clean_and_dump_data(list_url):
    
    # Creates directory for list's data, if it doesn't already exist.
    list_url_folder_name = list_url.split("/")[-1]    
    output_dir = create_output_directory(list_url_folder_name)
    
    # Load uncleaned data
    with codecs.open('outputs/output.json', 'r', encoding='utf-8') as f:
        books = json.load(f)
    
    # Dump uncleaned data into new file in list's directory
    with codecs.open(f'{output_dir}/uncleaned_data.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, sort_keys=False, indent=4, ensure_ascii=False)
    
    # Clean data for each book 
    for book in books:
        
        # clean ratings/review fields
        clean_ratings_and_reviews(book)
        
        # clean the rating histogram field
        clean_histogram(book)
        
        # clean authors fields
        clean_authors(book)
        
        # clean date fields
        clean_dates(book)
        
        # clean title fields
        clean_titles(book)

        # clean page_count, converting from str to int
        if book['page_count']:
            book['page_count'] = int(book['page_count'])
        
        # convert awards to a list (unsure if there exists any awards with a comma in them though)
        if book['awards']:
            book['awards'] = [award.strip() for award in book['awards'].split(",")]
    
    
    # Save cleaned data as CSV and JSON
    df = pd.DataFrame(books)
    df.to_csv(f'{output_dir}/cleaned_data.csv', index=False)
    
    with codecs.open(f'{output_dir}/cleaned_data.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, sort_keys=False, indent=4, ensure_ascii=False)
     
    # remove original file
    os.remove('outputs/output.json')