# Steps:
# 1. Store all perfume IDs
# 2. comment page url: "/itmcomment.php?id={}&o=u&page={}#/list".format(id, page_number)
# example: https://www.nosetime.com/itmcomment.php?id=251428&o=u&page=1#/list
# 3.
import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from main import *


def get_perfume_id():
    '''Get url from mongodb, only return number in the url
    '''
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    fragrance = client.fragrance
    raw_data_iterator = perfume_html.find()
    perfume_ids = []
    for f in raw_data_iterator:
        for v in re.findall(r'(/[0-9]*-)', f['url']):
            perfume_ids.append(v[1:-1])
    return perfume_ids


def scrape_one_first_page(perfume_id):
    '''
    Need to go through each first comment page, scrape the first page user id,
    and return all other page urls.
    Then go through each non-first page url to return the user id on other pages.
    '''
    count = 0
    attributes_list = []
    comment_url = "/itmcomment.php?id={}".format(perfume_id)
    response = get_html(comment_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find_all('div', {'class':'comment2'})
    for d in div:
        attributes = {}
        attributes['perfume_id'] = perfume_id # add perfume_id for each rating record
        attributes['rated_user_id'] = d.find('a')['href'] # member_id
        if d.find('span') != None:
            attributes['user_rating'] = int(d.find('span')['class'][1][2:]) # actual rating, 2nd element in a list
        else:
            attributes['user_rating'] = None
        attributes_list.append(attributes)
    return attributes_list

    with open('data/comment_pages.csv','a') as resultFile:
        wr = csv.writer(resultFile)
        for page in pages_raw[0].find_all('a')[1:-2]:
            wr.writerow([page['href']])

    time.sleep(10) # In case I got blocked
    count += 1
    if count % 10 == 0:
        print "Scraped {} page urls...".format(count)

if __name__ == '__main__':
    attributes_list = scrape_one_first_page('102121')
