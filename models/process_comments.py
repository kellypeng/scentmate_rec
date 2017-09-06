# After inspecting long comments, I think including short comments will make the
# topics more accurate, thus I scraped for short comments and combined short comments
# together with long comments in one dataframe
import numpy as np
import pandas as pd
import io
import jieba
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient


def short_comments_df(short_ratings_df):
    '''Takes in short_ratings dataframe, group by perfume id, return a dictionary
    with perfume id as key, all short comments of that perfume as values

    Parameter:
    ---------
    short ratings dataframe. Including perfume_id, rated_user_id, comments, url

    Return:
    -------
    dataframe, perfume_id as index, perfume short comments as another column
    '''
    scomments = defaultdict(list)
    for pid in short_ratings_df['perfume_id'].unique():
        df = short_ratings_df[(short_ratings_df['perfume_id'] == pid)]
        for c in df['short_comment']:
            scomments[pid].append(c)
    stacked = pd.DataFrame.from_dict(scomments, orient='index').stack().sum(level=0) # aggregate comments to perfume id
    short_comments_df = pd.DataFrame(stacked).rename(columns={0:'short_comments'}) # convert from pd series to dataframe
    return short_comments_df

def combine_comments(short_comments_df, long_comments_df):
    '''
    Join short comments df and long comments df, combine comments of each perfume id
    to a document.

    Parameter:
    ---------
    short_comments_df, long_comments_df

    Return:
    -------
    joined df, two columns, perfume id and all comments
    '''
    long_comments_df.set_index('perfume_id', inplace=True)
    long_comments_df['long_comments'] = long_comments_df['comments'].apply(','.join)
    all_comments = pd.merge(short_comments_df, long_comments_df, how='left', left_index=True, right_index=True)
    all_comments = all_comments.fillna('.')
    all_comments['all_comments'] = all_comments['short_comments'] + all_comments['long_comments']
    all_comments.drop(['comments', 'short_comments', 'long_comments', 'url'], axis=1, inplace=True)
    all_comments = all_comments.reset_index().rename(columns={'index':'perfume_id'})
    return all_comments



if __name__ == '__main__':
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    short_ratings = db.short_ratings
    short_ratings = pd.DataFrame(list(short_ratings.find({}, {'_id': 0})))
    perfume_comments = db.perfume_comments
    long_comments = pd.DataFrame(list(perfume_comments.find({}, {'_id': 0})))
    client.close()
    # Data preprocessing
    short_comments_df = short_comments_df(short_ratings)
    all_comments_df = combine_comments(short_comments_df, long_comments)
    # Write to csv
    all_comments_df.to_csv('../data/all_comments.csv', encoding='utf-8')
