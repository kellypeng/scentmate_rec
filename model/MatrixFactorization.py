import pandas as pd
import numpy as np
import graphlab as gl
import matplotlib.pyplot as plt
from sklearn.metrics import recall_score, precision_score, f1_score

def get_data(util):
    ''' Read utylity matrix into GraphLab SFrame '''
    sf = gl.SFrame(util)
    return sf

def train_test_split(sf):
    ''' Takes in SFrame, conduct train test split, keep every user exist
        in both training set and test set
    '''
    train, test = gl.recommender.util.random_split_by_user(sf, user_id='user_id', item_id='perfume_id')
    return train, test # this split is questionable, need to use LOOCV


if __name__ == '__main__':
    sf = get_data(util)
    train, test = train_test_split(sf)
    # Model 1
    m1 = gl.factorization_recommender.create(train,
                                            linear_regularization=0,
                                            user_id='user_id',
                                            item_id='perfume_id',
                                            target='user_rating',
                                            num_factors=5 # Number of latent factors.
                                            solver='als')


    #
    m2 = graphlab.factorization_recommender.create(sf,
                                                linear_regularization=1e-4,
                                                user_id='user',
                                                item_id='movie',
                                                target='rating',
                                                num_factors=15 # Number of latent factors.
                                                solver='als')
