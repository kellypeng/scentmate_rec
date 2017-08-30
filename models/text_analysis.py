# encoding=utf-8

import io
import numpy as np
import pandas as pd
import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient

def get_corpus(df):
    '''Build corpus from dataframe'''
    corpus = []
    for doc in df['comments']:
        corpus.append(doc[0])
    return corpus

def split_to_words(corpus):
    '''Use jieba to split Chinese text return a list string of words'''
    seg_list = []
    for doc in corpus:
        words = jieba.cut(doc)
        string = " ".join(words)
        seg_list.append(string)
    return seg_list

def get_cn_stopwords():
    '''Get stopwords file customized for perfume reviews, return a list of words'''
    with io.open('chinese_stopwords.txt', 'r', encoding='utf8') as f:
        stpwdlst = f.read().split()
    return stpwdlst

def get_tfidf_mat(seg_list, stop_words, max_features=1000):
    '''Get TFIDF matrix from tokenized documents corpus'''
    tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words,
                                       analyzer='word',
                                       max_features=max_features)
    tfidf_docs = tfidf_vectorizer.fit_transform(seg_list) # return a sparse matrix
    return tfidf_vectorizer, tfidf_docs

def find_top_features(k_features, tfidf_mat):
    '''
    Find top k features in each perfume

    Parameters:
    -----------
    1. number of features for each perfume
    2. TFIDF matrix converted from sparse matrix to 2d numpy array

    '''
    top_features_idx = np.empty([tfidf_mat.shape[0], k_features], dtype=int)
    top_features = np.empty([tfidf_mat.shape[0], k_features], dtype=object)
    for i, row in enumerate(tfidf_mat):
        top_features_idx[i] = np.argsort(row)[::-1][:k_features]
        top_features[i] = feature_names[top_features_idx[i]]
    return top_features, top_features_idx


if __name__ == '__main__':
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    collection = db.perfume_comments
    raw_df = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    client.close()

    # Tokenize
    stpwdlst = get_cn_stopwords()
    corpus = get_corpus(raw_df)
    seg_list = split_to_words(corpus)

    # Fit to TFIDF
    tfidf_vectorizer, tfidf_docs = get_tfidf_mat(seg_list, stop_words=stpwdlst, max_features=1000)
    feature_names = np.array(tfidf_vectorizer.get_feature_names())
    # print("Word List:")
    # print(feature_names)
    # print("TF IDF Vector：")
    # print(tfidf_docs.toarray())
    print("Top features for each perfume: ")
    top_features, top_features_idx = find_top_features(15, tfidf_docs.toarray())
    print(top_features)

    # Get top features corresponding perfume names, save to csv
    df = pd.DataFrame(top_features)
    df = df.reset_index()
    s = raw_df['perfume_id']
    s = s.reset_index()
    output = pd.merge(df, s, how='left', left_on='index', right_on='index')
    output.drop('index', axis=1, inplace=True)
    output.to_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/perfume_key_features.csv', encoding='utf-8')
