import re
import pandas as pd
import numpy as np
from pymongo import MongoClient

def train_test_split(df, n=3, frac=0.25):
    """Filter out users with >3 ratings.
    For users with 3 rating, put 2 ratings in training set, 1 rating in test set.
    For users with more than 3 ratings, divide the total number of ratings by 4,
    leave 1/4 in test set, all others in training set.

    Parameters:
    -----------
    User rating DataFrame, already only kept users with >2 ratings

    Returns:
    --------
    Training set, test set. DataFrame.
    """
    training_df = pd.DataFrame()
    test_df = pd.DataFrame()
    df.set_index('perfume_id', inplace=True) # to avoid additional index column
    for user_id in df['user_id'].unique():
        user_ratings = df[df['user_id'] == user_id]
        if user_ratings.groupby('user_id')['user_rating'].count().values == n:
            sample = user_ratings.sample(n=1, axis=0)
            test_df = test_df.append(sample)
            training_df = training_df.append(user_ratings.drop(sample.index, axis=0))
        else:
            sample = user_ratings.sample(frac=frac, axis=0)
            test_df = test_df.append(sample)
            training_df = training_df.append(user_ratings.drop(sample.index, axis=0))
    return training_df, test_df


if __name__ == '__main__':
    #utility = pd.read_csv('utility_matrix.csv')

    #training_df, test_df = train_test_split(utility)
    #training_df.to_csv('utility_train.csv', encoding='utf-8')
    #test_df.to_csv('utility_test.csv', encoding='utf-8')

    training_df = pd.read_csv('utility_train.csv')
    print "splitting training df..."
    train_train_df, train_valid_df = train_test_split(training_df, n=2, frac=0.34)
    train_train_df.to_csv('utility_train_train.csv', encoding='utf-8')
    train_valid_df.to_csv('utility_train_valid.csv', encoding='utf-8')
