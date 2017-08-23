# parse all perfume urls
import re
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
            if re.match("^(/pinpai/)", sublink.attrs['href']):
                attributes['brand'] = sublink.text
            if re.match("^(/xiangdiao/)", sublink.attrs['href']):
                attributes['theme'] = sublink.text
            if re.match("^(/qiwei/)", sublink.attrs['href']):
                attributes['note'].append(sublink.text)
            if re.match("(attrib&word)", sublink.attrs['href']):
                attributes['gender'] = sublink.text
            if re.match('(/tiaoxiangshi/)', sublink.attrs['href']):
                attributes['perfumer'] = sublink.text
            if re.match('(tag&word)', sublink.attrs['href']):
                attributes['tags'].append(sublink.text)
    attributes['item_name'] = soup.find('h1').text
    attributes['url'] = url
    return attributes



if __name__ == '__main__':
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    fragrance = client.fragrance
    perfume_html = fragrance.perfume_html
    perfumes = fragrance.perfumes
    raw_data_iterator = perfume_html.find() # retrieve all from mongo
    print "Parsing data and store into MongoDB..."
    for raw in raw_data_iterator:
        attributes = get_attributes(raw)
        perfumes.insert_one(attributes) # insert one by one into mongo
    print "Done! Everything is parsed into usable format!"
    client.close()
