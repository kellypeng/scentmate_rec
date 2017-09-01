import io
import numpy as np
import pandas as pd
import jieba
import jieba.posseg as pseg
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

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

def get_perfume_stopwords():
    '''Get stopwords file customized for perfume reviews, return a list of words'''
    with io.open('chinese_stopwords.txt', 'r', encoding='utf8') as f:
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
        print 'topic', i
        print '-->', ' '.join(vocabulary[top_five])
        label = raw_input('please label this topic: ')
        hand_labels.append(label)
        print
    return hand_labels

def main():
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    collection = db.perfume_comments
    raw_df = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    client.close()
    #############################################################
    # Tokenize corpus
    stpwdlst = get_perfume_stopwords()
    corpus = get_corpus(raw_df)
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
    no_topics = 8
    # Run NMF
    nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf_docs)
    # Run LDA
    # lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf_docs)

    #############################################################
    no_top_words = 20
    print("Topics found by NMF: ")
    display_topics(nmf, tfidf_feature_names, no_top_words)
    print("NMF left W matrix: ")
    W = nmf.fit_transform(tfidf_docs)
    print("NMF right H matrix: ")
    H = nmf.components_
    print('reconstruction error:', nmf.reconstruction_err_)
    # print('='*40)
    # print("Topics found by LDA: ")
    # display_topics(lda, tf_feature_names, no_top_words)


if __name__ == '__main__':
    main()
