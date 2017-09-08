import re
import os
import sys
from collections import defaultdict
from bs4 import BeautifulSoup
from pymongo import MongoClient


def get_attributes(mongo_document):
    '''
    Input: perfume webpage html content
    Output: a dictionary of what I need for the item matrix
    '''
    html = mongo_document['html']
    url = mongo_document['url']
    soup = BeautifulSoup(html, 'html.parser')
    attributes = defaultdict(list)
    for link in soup.find('ul', {'class': 'item_info'}):
        for sublink in link.find_all('a', href=True):
            if re.match('(/pinpai/)', sublink.attrs['href']):
                attributes['brand'] = sublink.text
            if re.match('(/xiangdiao/)', sublink.attrs['href']):
                attributes['theme'] = sublink.text
            if re.match('(/qiwei/)', sublink.attrs['href']):
                attributes['note'].append(sublink.text)
            if re.match('(/tiaoxiangshi/)', sublink.attrs['href']):
                attributes['perfumer'] = sublink.text
            if re.search('(field=attrib)', sublink.attrs['href']): # re.match() will match from the beginning, re.search() looks for any location where this RE matches
                attributes['gender'].append(sublink.text)
            if re.search('(field=tag)', sublink.attrs['href']):
                attributes['tags'].append(sublink.text)
    attributes['perfume_id'] = re.findall(r'(/[0-9]*-)', url)[0][1:-1]
    attributes['item_name'] = soup.find('h1').text
    attributes['url'] = url
    return attributes


def get_comments(mongo_document):
    '''
    Input: perfume webpage html content
    Output: a dictionary of perfume url and perfume comments
    '''
    html = mongo_document['html']
    url = mongo_document['url']
    soup = BeautifulSoup(html, 'html.parser')
    attributes = defaultdict(list)
    if soup.find('div', {'class': 'hfshow'}) != None:
        for discuss in soup.find_all('div', {'class': 'hfshow'}):
            attributes['comments'].append(discuss.text)
            attributes['perfume_id'] = re.findall(r'(/[0-9]*-)', url)[0][1:-1]
            attributes['url'] = url
        return attributes



if __name__ == '__main__':
    fragrance_un = os.environ.get('FRAGRANCE_UN')
    fragrance_pw = os.environ.get('FRAGRANCE_PW')
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(fragrance_un, fragrance_pw))
    fragrance = client.fragrance
    perfume_html = fragrance.perfume_html
    perfume_features = fragrance.perfume_features # get attributes
    perfume_comments = fragrance.perfume_comments # get perfume comments
    raw_data_iterator = perfume_html.find() # retrieve all from mongo
    print "Parsing data and store into MongoDB..."
    ## Parse perfume attributes
    for raw in raw_data_iterator:
        attributes = get_attributes(raw)
        perfume_features.insert_one(attributes) # insert one by one into mongo
    print "Done! Everything is parsed into usable format!"
    client.close()

    ### Parse perfume comments
    count = 0
    for raw in raw_data_iterator:
        attributes = get_comments(raw)
        if attributes != None:
            perfume_comments.insert_one(attributes)
            count += 1
            if count % 10 == 0:
                print "Inserted {} comments".format(count)
    print 'Done! You got all the comments!'
    client.close()
