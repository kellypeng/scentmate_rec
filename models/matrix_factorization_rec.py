import sys
import pandas as pd
import numpy as np
import graphlab as gl
from time import time
from pymongo import MongoClient
from sklearn.model_selection import LeaveOneOut
import model_main as mm

def get_data(util):
    ''' Read utylity matrix into GraphLab SFrame '''
    sf = gl.SFrame(util)
    return sf

def train_test_split(sf):
    ''' Takes in SFrame, conduct train test split, keep every user exist
        in both training set and test set
        * Note: Dan does not suggest using this method
    '''
    train, test = gl.recommender.util.random_split_by_user(sf, user_id='user_id', item_id='perfume_id')
    return train, test # this split is questionable, need to use LOOCV

def mf_model(data, num_factors=10, linear_regularization=1e-4):
    '''Fit matrix factorization model'''
    return gl.factorization_recommender.create(data,
                                            linear_regularization=linear_regularization,
                                            user_id='user_id',
                                            item_id='perfume_id',
                                            target='user_rating',
                                            num_factors=num_factors, # Number of latent factors.
                                            solver='als')

def leave_one_out_cv(data, timing=False):
    '''Conduct leave one out cross validation for matrix factorization model
    Input:
    ------
    Utility matrix

    Output:
    ------
    RMSE calculated based on LOOCV

    Failed to run!!!!
    '''
    start_time = time()
    loo = LeaveOneOut()
    rmse = []
    count = 0
    # for train_index, valid_index in loo.split(sf):
    #     m = mf_model(sf[train_index])
    folds = gl.cross_validation.KFold(data, 28309)
    for train, valid in folds:
        m = mf_model(sf)
        rmse.append(m.evaluate_rmse(valid, target='user_rating')['rmse_overall'])
        count += 1
        if count % 100 == 0:
            print "Leave one out cross validation is getting to {} folds..".format(count)
    if timing:
        print ("Run time: %s seconds" % (time() - start_time))
    return np.mean(rmse)


if __name__ == '__main__':
    mongo_user_name, mongo_pwd = sys.argv[1], sys.argv[2]
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(mongo_user_name, mongo_pwd))
    db = client.fragrance
    collection = db.ratings_trial2
    utility_matrix = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    util = mm.prepare_util_mat(utility_matrix)
    util_mf = mm.remove_user(util) # remove users with only 1 rating
    sf = get_data(util_mf) # transform into SFrame
    # train, test = train_test_split(sf)
    # Model 1, without regularization
    # m1 = gl.factorization_recommender.create(train,
    #                                         linear_regularization=0,
    #                                         user_id='user_id',
    #                                         item_id='perfume_id',
    #                                         target='user_rating',
    #                                         num_factors=5 # Number of latent factors.
    #                                         solver='als')

    # # Model 2, with regularization
    # m2 = graphlab.factorization_recommender.create(sf,
    #                                             linear_regularization=1e-4,
    #                                             user_id='user',
    #                                             item_id='movie',
    #                                             target='rating',
    #                                             num_factors=15 # Number of latent factors.
    #                                             solver='als')

    # rmse = leave_one_out_cv(sf, timing=True)
