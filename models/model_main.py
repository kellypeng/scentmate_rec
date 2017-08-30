#coding: utf-8
import re
import sys
import pandas as pd
import numpy as np
from pymongo import MongoClient


def prepare_item_mat(mongo_user_name, mongo_pwd):
    '''Takes in MongoDB perfume features table, returns item matrix

    Input:
    ------
    MongoDB fragrance database, perfume_new collection

    Output:
    ------
    Item matrix with rows as perfumes, columns as perfume features,
    including notes, tags, gender
    '''
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(mongo_user_name, mongo_pwd))
    db = client.fragrance
    collection = db.perfume_features
    raw_df = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    client.close()
    df = raw_df.drop_duplicates('perfume_id')
    df.set_index(df['perfume_id'], inplace=True)
    note = df['note'].apply(pd.Series) # 653 notes
    note_matrix = pd.get_dummies(note.apply(pd.Series).stack()).sum(level=0).rename(columns = lambda x : 'note_' + x)
    tags = df['tags'].apply(pd.Series) # 75 tags
    tag_matrix = pd.get_dummies(tags.apply(pd.Series).stack()).sum(level=0).rename(columns = lambda x: 'tag_' + x)
    theme = df['theme'].apply(pd.Series) # 31 themes
    theme_matrix = pd.get_dummies(theme.apply(pd.Series).stack()).sum(level=0).rename(columns = lambda x: 'theme_' + x)
    gender = df['gender'].apply(pd.Series)
    gender_matrix = pd.get_dummies(gender.apply(pd.Series).stack()).sum(level=0).rename(columns = lambda x: 'gender_' + x)
    item_matrix = note_matrix.join(tag_matrix).join(theme_matrix).join(gender_matrix) # join together the four matrices
    item_matrix.fillna(0, inplace=True) # fill in null values with 0
    return item_matrix


def prepare_util_mat(utility_matrix):
    '''
    Input:
    ------
    Takes in ratings data read into pandas dataframe, then
    - Remove duplicates
    - Remove users who only have 1 rating
    - Drop null values
    - Parse user_id, drop original rated_user_id

    Output:
    ------
    - A pandas dataframe with 3 columns: perfume_id, user_id, and user_rating
    '''
    utility_matrix = utility_matrix.drop_duplicates()
    utility_matrix.dropna(axis=0, inplace=True) # drop null values, wait, is it appropriate to drop?
    utility_matrix['user_id'] = utility_matrix['rated_user_id'].str.extract('(\d+)').astype(int) # extract user_id number
    utility_matrix.drop('rated_user_id', axis=1, inplace=True) # drop original user_id column
    return utility_matrix


def remove_user(utility_matrix):
    '''
    Takes in utility matrix, removes users with only 1-2 rating record
    Returns new utility matrix
    '''
    return utility_matrix[utility_matrix.groupby('user_id')['perfume_id'].transform(len) > 2]


def rmse(y_true, y_pred):
    ''' Compute Root-mean-squared-error '''
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def write_pickle(filename, model):
    """
    Write the final model to a pickle file
    Parameters
    ----------
    filename : String
    model : recommender model instance
    Returns
    ----------
    Nothing
    """
    with open(filename, 'w') as f:
        pickle.dump(model, f)

def train_test_split():
    pass


if __name__ == '__main__':
    mongo_user_name, mongo_pwd = sys.argv[1], sys.argv[2]
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(mongo_user_name, mongo_pwd))
    db = client.fragrance
    collection = db.ratings_trial2
    utility_matrix = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    util = prepare_util_mat(utility_matrix)
    util = remove_user(util) # remove users with less than 2 ratings!!
    util.set_index('perfume_id', inplace=True)
    # item_matrix = prepare_item_mat(mongo_user_name, mongo_pwd)
    util.to_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/utility_matrix.csv', encoding='utf-8')
