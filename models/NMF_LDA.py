# Need to run in python 3 environment
import io
import os
import numpy as np
import pandas as pd
import jieba
import jieba.posseg as pseg
import short_ratings as sr
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

def get_corpus(df):
    '''Build corpus from dataframe'''
    corpus = []
    for doc in df['all_comments']:
        corpus.append(doc)
    return corpus

def split_to_words(corpus):
    '''Use jieba to split Chinese text return a list string of words'''
    seg_list = []
    for doc in corpus:
        words = jieba.cut(doc)
        string = " ".join(words)
        seg_list.append(string)
    return seg_list

def get_perfume_stopwords():
    '''Get stopwords file customized for perfume reviews, return a list of words'''
    with io.open('perfume_cn_stopwords.txt', 'r', encoding='utf8') as f:
        stpwdlst = f.read().split()
    return stpwdlst

def get_vectorized_mat(seg_list, use_tfidf, stop_words, max_features=1000):
    '''Get TFIDF or TF matrix from tokenized documents corpus
    If use_tfidf is True --> TFIDF Vectorizer
    If user_tfidf is False --> Count Vectorizer'''
    Vectorizer = TfidfVectorizer if use_tfidf else CountVectorizer
    vectorizer_model = Vectorizer(stop_words=stop_words,
                           analyzer='word',
                           max_features=max_features)
    vec_docs = vectorizer_model.fit_transform(seg_list) # return a sparse matrix
    return vectorizer_model, vec_docs

def display_topics(model, feature_names, no_top_words):
    '''Display topics generated from NMF and LDA mdoel'''
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

def hand_label_topics(H, vocabulary):
    '''
    Print the most influential words of each latent topic, and prompt the user
    to label each topic. The user should use their humanness to figure out what
    each latent topic is capturing.
    '''
    hand_labels = []
    for i, row in enumerate(H):
        top_five = np.argsort(row)[::-1][:20]
        print('topic', i)
        print('-->', ' '.join(vocabulary[top_five]))
        label = raw_input('please label this topic: ')
        hand_labels.append(label)
        print
    return hand_labels

def get_keywords_mat():
    '''
    Get 12 topics from LDA, add keywords features to rated perfumes.
    Return a dataframe with perfume_id and keywords

    Parameters:
    ----------
    LDA fit_transform(tf_docs)

    Returns:
    ------
    perfume_keywords_df. index: perfume_id, columns: keyword names, values: 1/0
    '''
    # manually label 12 topics generatd from LDA
    topic_dict = {0: (u'甜美', u'甜蜜', u'甜味', u'美食', u'香草', u'柔滑'),
                  1: (u'温柔', u'优雅', u'成熟', u'女人', u'脂粉', u'性感'),
                  2: (u'清新', u'柑橘', u'经典', u'琥珀', u'老香', u'东方调'),
                  3: (u'白花系', u'清新', u'淡雅', u'茶香', u'平易近人', u'邻家女孩'),
                  4: (u'少女', u'果香', u'甜美', u'可爱', u'活泼', u'甜蜜'),
                  5: (u'清新', u'干净', u'夏天', u'清爽', u'舒服', u'清凉'),
                  6: (u'玫瑰', u'温柔', u'少女', u'牡丹', u'女人味', u'清新'),
                  7: (u'辛辣', u'温暖', u'男人味', u'温柔', u'稳重', u'成熟'),
                  8: (u'东方调', u'焚香', u'神秘', u'辛辣', u'深沉', u'柔和'),
                  9: (u'美食', u'甜蜜', u'温暖', u'甜味', u'浓郁', u'冬天'),
                  10: (u'无花果', u'清新', u'青草', u'绿叶调', u'植物', u'夏天'),
                  11: (u'经典', u'大牌', u'奢华', u'广为人知', u'商业香', u'广告多见')}
    perfume_kw_dict = {}
    for idx, item in enumerate(lda_left):
        perfume_kw_dict[idx] = topic_dict[np.argmax(item)]
    # convert dictionary to dataframe for join convenience
    perfume_topic_df = pd.DataFrame.from_dict(perfume_kw_dict, orient='index')
    perfume_topic_df = perfume_topic_df.fillna(' ')
    keywords_matrix = pd.get_dummies(perfume_topic_df.apply(pd.Series).stack() \
                      ).sum(level=0).rename(columns = lambda x: 'keywords_' + x)
    perfume_keywords_df = all_comments_df.join(keywords_matrix)
    perfume_keywords_df.drop('all_comments', axis=1, inplace=True)
    perfume_keywords_df.set_index('perfume_id', inplace=True)
    return perfume_keywords_df


if __name__ == '__main__':
    fragrance_un = os.environ.get('FRAGRANCE_UN')
    fragrance_pw = os.environ.get('FRAGRANCE_PW')
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(fragrance_un, fragrance_pw))
    db = client.fragrance
    short_ratings = db.short_ratings
    short_ratings = pd.DataFrame(list(short_ratings.find({}, {'_id': 0})))
    perfume_comments = db.perfume_comments
    long_comments = pd.DataFrame(list(perfume_comments.find({}, {'_id': 0})))
    client.close()
    # Data preprocessing
    short_comments_df = sr.short_comments_df(short_ratings)
    all_comments_df = sr.combine_comments(short_comments_df, long_comments)
    #############################################################
    # Tokenize corpus
    stpwdlst = get_perfume_stopwords()
    corpus = get_corpus(all_comments_df)
    seg_list = split_to_words(corpus)

    #############################################################
    # NMF is able to use tf-idf, thus fit documents to TFIDF
    tfidf_vectorizer, tfidf_docs = get_vectorized_mat(seg_list,
                                                      use_tfidf=True,
                                                      stop_words=stpwdlst,
                                                      max_features=1000)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    #############################################################
    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model, thus fit to CountVectorizer
    countvectorizer, tf_docs = get_vectorized_mat(seg_list,
                                                  use_tfidf=False,
                                                  stop_words=stpwdlst,
                                                  max_features=1000)
    tf_feature_names = countvectorizer.get_feature_names()

    #############################################################
    no_topics = 12
    # Run NMF
    nmf = NMF(n_components=no_topics, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf_docs)
    # Run LDA
    lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf_docs)

    #############################################################
    no_top_words = 20
    print("Topics found by NMF: ")
    display_topics(nmf, tfidf_feature_names, no_top_words)
    print('='*40)
    print("Topics found by LDA: ")
    display_topics(lda, tf_feature_names, no_top_words)
    # End up with LDA with 12 topics
    lda_left = lda.fit_transform(tf_docs)
