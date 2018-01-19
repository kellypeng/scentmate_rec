# Steps:
# 1. Store all perfume IDs
# 2. comment page url: "/itmcomment.php?id={}&o=u&page={}#/list".format(id, page_number)
# example: https://www.nosetime.com/itmcomment.php?id=251428&o=u&page=1#/list
# 3. Insert data to mongodb ratings collection
import os
import csv
import time
import re
import sys
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from main import *


def get_perfume_id():
    """Get url from mongodb, only return number in the url
    """
    perfume_html = fragrance.perfume_html
    raw_data_iterator = perfume_html.find()
    perfume_ids = []
    for f in raw_data_iterator:
        for v in re.findall(r'(/[0-9]*-)', f['url']):
            perfume_ids.append(v[1:-1])
    return perfume_ids

def read_data(filename):
    with open(filename) as f:
        lines = f.read().split(',')
    return lines

def scrape_one_page(perfume_id):
    """
    Need to go through each first comment page, scrape the first page user id,
    and return all other page urls.
    Then go through each non-first page url to return the user id on other pages.
    """
    attributes_list = []
    comment_url = "/itmcomment.php?id={}".format(perfume_id)
    response = get_html(comment_url)
    if response != None:
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find_all('div', {'class':'comment2'})
        for d in div:
            attributes = {}
            attributes['perfume_id'] = perfume_id # add perfume_id for each rating record
            attributes['rated_user_id'] = d.find('a')['href'] # member_id
            attributes['short_comment'] = d.find('div', {'class': 'hfshow1'}).text
            if d.find('span') != None:
                attributes['user_rating'] = int(d.find('span')['class'][1][2:]) # actual rating, 2nd element in a list
            else:
                attributes['user_rating'] = None
            attributes_list.append(attributes)
        if len(attributes_list) > 0:
            print "Perfume ID {} has reviews. Inserting rating to MongoDB".format(perfume_id)
            short_ratings.insert_many(attributes_list) # insert to mongodb
        else:
            print "Perfume ID {} has no reviews.".format(perfume_id)
        # store pages url to comment_pages.csv
        pages = soup.find('div', {'class':'next_news'})
        if pages != None:
            print "Writing page urls to csv file..."
            with open('data/comment_pages_ratings_0901.csv','a') as resultFile:
                wr = csv.writer(resultFile)
                for page in pages.find_all('a')[1:]:
                    wr.writerow([page['href']])
        time.sleep(10) # In case I got blocked
    else:
        print "This url does not exist." # Handle Attribute Error: Nonetype does not have "text"
        pass


def scrape_all_pages(page_url):
    attributes_list = []
    perfume_id = re.findall(r'(=[0-9]*&)', page_url)[0][1:-1] # parse url to get id
    response = get_html(page_url)
    if response != None:
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find_all('div', {'class':'comment2'})
        for d in div:
            attributes = {}
            attributes['perfume_id'] = perfume_id # add perfume_id for each rating record
            attributes['rated_user_id'] = d.find('a')['href'] # member_id
            attributes['short_comment'] = d.find('div', {'class': 'hfshow1'}).text
            if d.find('span') != None:
                attributes['user_rating'] = int(d.find('span')['class'][1][2:]) # actual rating, 2nd element in a list
            else:
                attributes['user_rating'] = None
            attributes_list.append(attributes)
        if len(attributes_list) > 0:
            print "Perfume ID {} has reviews. Inserting rating to MongoDB".format(perfume_id)
            short_ratings.insert_many(attributes_list) # insert to mongodb
        else:
            print "Perfume ID {} has no reviews.".format(perfume_id)
        pass


if __name__ == '__main__':
    print "Scraping for rating data..."
    fragrance_un = os.environ.get('FRAGRANCE_UN')
    fragrance_pw = os.environ.get('FRAGRANCE_PW')
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(fragrance_un, fragrance_pw))
    fragrance = client.fragrance
    short_ratings = fragrance.short_ratings
    print "Get all perfume id to a list..."
    # perfume_ids = get_perfume_id()
    perfume_ids = read_data('data/rated_perfume_id.csv') # 21,023 perfumes
    n1, n2 = sys.argv[1], sys.argv[2]
    print "Scraping first page user ratings..."
    count = 0
    for pid in perfume_ids[int(n1):int(n2)]: # altogether we have 22,358 perfumes
        scrape_one_page(pid)
        print "Scraped {} first page urls...".format(count)
        count += 1

    print "Done inserting first page ratings to MongoDB!"
    print "-"*40
    print "Scraping non-first page comment urls..."
    page_urls = get_url_list('data/comment_pages_ratings_deduped.csv')
    count2 = 0
    for page in page_urls:
        scrape_all_pages(page)
        print "Scraped {} non-first page urls...".format(count2)
        count2 += 1
    print "Woohoooo!! Done inserting non-first page ratings to mongodb! "
