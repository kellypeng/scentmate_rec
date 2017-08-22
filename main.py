# Switch to Chinese website instead
import csv
import requests
import time
import sys
from urllib2 import urlopen, Request, HTTPError
from bs4 import BeautifulSoup # Used to parse the HTML content of web pages
from fake_useragent import UserAgent


def read_data(filename):
    with open(filename) as f:
        lines = f.read().split(',')
    return lines

def get_html(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
    #            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get('https://www.nosetime.com'+url, headers)
    except HTTPError as e:
        print "Url Can not be found"
        return None
    except requests.exceptions.Timeout:
        print "Timeout error" # Maybe set up for a retry, or continue in a retry loop
        return None
    except requests.exceptions.TooManyRedirects:
        print "TooManyRedirects error" # Tell the user their URL was bad and try a different one
        return None
    except requests.exceptions.RequestException as e:
        print e # catastrophic error. bail.
        return None
    return response

def get_brand_urls():
    '''
    Input: list of brand name start letter webpage urls
    Output: perfume brand name urls in a list
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
    brands = []
    for url in lst:
        response = get_html(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find_all('a', {'class': 'imgborder'})
        for r in result:
            brands.append(r.attrs['href'])
        time.sleep(10) # In case I got blocked
        count += 1
        if count % 10 == 0:
            print "Scraped {} urls...".format(count)
    return brands

def scrape_first_page(brand_urls, range_start, range_end):
    '''
    Need to go through each brand_url, scrape the first page, then return all other page_urls.
    Then go through each page_url to return the fragrance names on other pages.
    '''
    count = 0
    pages_list = []
    for url in brand_urls[range_start:range_end]:
        response = get_html(url)
        if response == None:
            print "Get HTML break at #{} url.".format(count)
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        perfume = soup.find_all('a', {'class': 'imgborder'}) # scrape all 1st pages

        with open('data/perfumes_2.csv','a') as resultFile: # go through each page, fetch perfume urls and store to csv
            wr = csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])
        # After scraping every first page, let's scrape page urls
        pages_raw = soup.find_all('div', {'class': 'next_news'})
        for page in pages_raw[0].find_all('a')[1:-2]:
            pages_list.append(page['href'])
        time.sleep(10) # In case I got blocked
        count += 1
        if count % 10 == 0:
            print "Scraped {} page urls...".format(count)
    print "Done writing perfume urls to csv! Congrats! Save returned pages_list!"
    return pages_list

def scrape_other_pages(pages_list):
    '''
    Go through each page other than the first page, scrape perfume urls
    '''
    count = 0
    for url in pages_list:
        response = get_html(url)
        if response == None:
            print "Get HTML break at #{} url.".format(count)
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
            print "Scraped {} page urls...".format(count)
        if count % 90 == 0:
            print "Take a nap for 8 minutes...Please don't block me!!!"
            time.sleep(60*8)
    print "Done writing perfume urls to csv!"



if __name__ == '__main__':
    # brands = get_brand_urls()
    # print "Writing csv file..."
    # with open('data/brands.csv','wb') as resultFile:
    #     wr = csv.writer(resultFile, dialect='excel')
    #     wr.writerow(brands)
    # print "Finished writing csv file..."
    brands = read_data('data/brands.csv')
    n1, n2 = sys.argv[1], sys.argv[2]
    pages_list = scrape_first_page(brands, int(n1), int(n2))
    # after brands are scraped...
    # perfumes = read_data('data/perfumes.csv')
    # scrape_other_pages(pages_list)
