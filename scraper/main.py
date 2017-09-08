# Switch to Chinese website instead
import re
import os
import csv
import requests
import time
import sys
from urllib2 import urlopen, Request, HTTPError
from bs4 import BeautifulSoup # Used to parse the HTML content of web pages
from fake_useragent import UserAgent
from pymongo import MongoClient

fragrance_un = os.environ.get('FRAGRANCE_UN')
fragrance_pw = os.environ.get('FRAGRANCE_PW')

def read_data(filename):
    with open(filename) as f:
        lines = f.read().split(',')
    return lines


def get_html(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get('https://www.nosetime.com'+url, headers)
    except HTTPError as e:
        print ("Url Can not be found")
        return None
    except requests.exceptions.Timeout:
        print ("Timeout error") # Maybe set up for a retry, or continue in a retry loop
        return None
    except requests.exceptions.TooManyRedirects:
        print ("TooManyRedirects error") # Tell the user their URL was bad and try a different one
        return None
    except requests.exceptions.RequestException as e:
        print e # catastrophic error. bail.
        return None
    return response


def get_brand_urls():
    '''
    Input:
    ------
    List of brand name start letter webpage urls

    Output:
    ------
    Perfume brand name urls in a list
    A dictionary of perfume EN and CN names
    '''
    lst = ['/pinpai/2-a.html','/pinpai/3-b.html','/pinpai/4-c.html',
           '/pinpai/5-d.html','/pinpai/6-e.html','/pinpai/7-f.html',
           '/pinpai/8-g.html','/pinpai/9-h.html','/pinpai/10-i.html',
           '/pinpai/11-j.html','/pinpai/12-k.html','/pinpai/13-i.html',
           '/pinpai/14-m.html','/pinpai/15-n.html','/pinpai/16-o.html',
           '/pinpai/17-p.html','/pinpai/18-q.html','/pinpai/19-r.html',
           '/pinpai/20-s.html','/pinpai/21-t.html','/pinpai/22-u.html',
           '/pinpai/23-v.html','/pinpai/24-w.html','/pinpai/25-x.html',
           '/pinpai/26-y.html','/pinpai/27-z.html']
    count = 0
    brand_urls = []
    brand_names = {}
    for url in lst:
        response = get_html(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find_all('a', {'class': 'imgborder'})
        for r in result:
            brand_urls.append(r.attrs['href'])
            name = r.next_sibling.text
            split = re.split(r'([a-zA-Z]+)', name)
            brand_names[split[0]] = ''.join(split[1:])
        time.sleep(5) # In case I got blocked
        print ("Scraped {} urls...".format(count))
        count += 1
    return brand_urls, brand_names


def scrape_first_page(brand_urls, range_start, range_end):
    '''
    Need to go through each brand_url, scrape the first page, then return all other page_urls.
    Then go through each page_url to return the fragrance names on other pages.
    '''
    count = 0
    for url in brand_urls[range_start:range_end]:
        response = get_html(url)
        if response == None:
            print ("Get HTML break at #{} url.".format(count))
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        perfume = soup.find_all('a', {'class': 'imgborder'}) # scrape all 1st pages
        pages_raw = soup.find_all('div', {'class': 'next_news'})

        with open('data/perfumes_2.csv','a') as resultFile: # go through each page, fetch perfume urls and store to csv
            wr = csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])

        with open('data/pages.csv','a') as resultFile:
            wr = csv.writer(resultFile)
            for page in pages_raw[0].find_all('a')[1:-2]:
                wr.writerow([page['href']])

        time.sleep(10) # In case I got blocked
        count += 1
        if count % 10 == 0:
            print "Scraped {} page urls...".format(count)
    print ("Done writing perfume urls to csv! Congrats! Save returned pages_list!")


def scrape_other_pages(pages_list):
    '''
    Go through each page other than the first page, scrape perfume urls

    Input: A list of page urls
    Output: Append perfume url to perfumes_2.csv
    '''
    count = 0
    for url in pages_list:
        response = get_html(url)
        if response == None:
            print("Get HTML break at #{} url.".format(count))
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        perfume = soup.find_all('a', {'class': 'imgborder'})
        with open('data/perfumes_2.csv','a') as resultFile: # go through each page, fetch perfume urls and store to csv
            wr = csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])
        time.sleep(10) # In case I got blocked
        count += 1
        if count % 10 == 0:
            print("Scraped {} page urls...".format(count))
        if count % 90 == 0:
            print("Take a nap for 8 minutes...Please don't block me!!!")
            time.sleep(60*8)
    print("Done writing perfume urls to csv!")


def scrape_perfume_page(perfume_urls):
    '''Scrape one page html and store into MongoDB

    Input: list of perfume urls
    Output: url, html, stored into MongoDB ec2 instance
    '''
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(fragrance_un, fragrance_pw))
    fragrance = client.fragrance
    perfume_html = fragrance.perfume_html
    count = 0
    for url in perfume_urls:
        html_text = get_html(url).text
        if html_text == None:
            print("Get HTML break at #{} url.".format(count))
            break
        perfume_html.insert({'url': url, 'html': html_text})
        count += 1
        if count % 100 == 0:
            print("Scraped {} pages html...".format(count))
    client.close()


def get_url_list(filename):
    '''Convert a csv file with \r\n delimiter to a list of strings

    Input: csv file with \r\n delimeter
    Output: a list of urls
    '''
    f = open(filename)
    data = []
    for line in f:
        data_line = line.rstrip().split('\r\n')
        data.append(data_line[0])
    return data


if __name__ == '__main__':
    brands, brand_names = get_brand_urls()
    print("Writing csv file...")
    # with open('data/brands.csv','wb') as resultFile:
    #     wr = csv.writer(resultFile, dialect='excel')
    #     wr.writerow(brands)
     with open('../data/brand_names.csv','wb') as resultFile:
         wr = csv.writer(resultFile, dialect='excel')
         for key, value in brand_names.items():
             wr.writerow([key.encode('utf-8'), value.encode('utf-8')])
    # print "Finished writing csv file..."
    # brands = read_data('data/brands.csv')
    # n1, n2 = sys.argv[1], sys.argv[2]
    # pages_list = scrape_first_page(brands, int(n1), int(n2))
    # after brands are scraped...
    # perfumes = read_data('data/perfumes.csv')
    # print "Getting pages list..."
    # get_pages_list(brands, int(n1), int(n2)) # deprecated function

    # pages = get_url_list('data/pages.csv')
    # print "Scraping other pages for perfume urls..."
    # scrape_other_pages(pages)
    # print "Converting perfumes csv file to a list..."
    # perfumes = get_url_list('data/perfumes_2.csv')
    # print "Inserting perfumes html to MongoDB..."
    # scrape_perfume_page(perfumes)
    # print "Woohoo, done! Congrats! "
