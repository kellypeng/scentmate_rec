import sys
import pandas as pd
import numpy as np
import graphlab as gl
import matplotlib.pyplot as plt
from time import time
import model_main as mm


def mf_model(data, similarity_type='cosine', only_top_k=64):
    """Fit matrix factorization model"""
    return gl.recommender.item_similarity_recommender.create(data,
                                                            user_id='user_id',
                                                            item_id='perfume_id',
                                                            target='user_rating',
                                                            nearest_items=None, # A set of each item’s nearest items. When provided, this overrides the similarity computed by only_top_k
                                                            similarity_type=similarity_type,
                                                            threshold=0.001,
                                                            only_top_k=only_top_k)

def tune_only_top_k(train, test):
    """Find the optimum number of Number of similar items to store for each item
    and calculate RMSE against train test data"""
    test_rmse = []
    train_rmse = []
    for n in xrange(30, 200, 5):
        m = mf_model(train, only_top_k=n)
        test_rmse.append(m.evaluate_rmse(test, target='user_rating')['rmse_overall'])
        train_rmse.append(m.training_rmse)
    plt.plot(test_rmse, color='r', label='Test RMSE')
    plt.plot(train_rmse, color='b', label='Train RMSE')
    plt.xlabel('Number of Factors')
    plt.xlabel('RMSE')


if __name__ == '__main__':
    train = pd.read_csv('../data/train_valid_test/utility_train_train.csv')
    valid = pd.read_csv('../data/train_valid_test/utility_train_valid.csv')
    # convert to SFrame
    train = gl.SFrame(train)
    valid = gl.SFrame(valid)
    tune_only_top_k(train, valid)
    plt.show()

    #### Try random_split_by_user in graphlab
