import sys
import numpy as np
import pandas as pd
import model_main as mm
from scipy import sparse
from time import time
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity


class ItemItemRecommender(object):

    def __init__(self, neighborhood_size):
        self.neighborhood_size = neighborhood_size

    def fit(self, ratings_contents):
        '''
        Implement the model and fit it to the data passed as an argument.

        Store objects for describing model fit as class attributes.
        '''
        self.ratings_contents = ratings_contents # 3 columns dataframe, user_id, perfume_id, rating
        self.ratings_pivot = pd.pivot_table(self.ratings_contents, values='user_rating', \
                             index='user_id', columns='perfume_id', fill_value=0)
        self.ratings_mat = sparse.csr_matrix(self.ratings_pivot.values) # sparse matrix, shape 3750 by 3116
        self.n_users = ratings_mat.shape[0]
        self.n_items = ratings_mat.shape[1]
        self.item_sim_mat = cosine_similarity(self.ratings_mat.T) # 3,116 by 3,116, pairwise similarity between perfumes
        self._set_neighborhoods()

    def _set_neighborhoods(self):
        '''
        Get the items most similar to each other item.

        Should set a class attribute with a matrix that is has
        number of rows equal to number of items and number of
        columns equal to neighborhoodsghborhood size. Entries of this matrix
        will be indexes of other items.

        You will call this in your fit method.
        '''
        least_to_most_sim_indexes = np.argsort(self.item_sim_mat, 1)
        self.neighborhoods = least_to_most_sim_indexes[:, -self.neighborhood_size:]

    def pred_one_user(self, user_id, report_run_time=False):
        '''
        Accept user id as arg. Return the predictions for a single user.

        Optional argument to specify whether or not timing should be provided
        on this operation.
        '''
        start_time = time()
        items_rated_by_this_user = self.ratings_pivot.loc[user_id].nonzero()[0] # use loc to return row index of the user_id, return an 1d array of rated perfume column indices
        # Just initializing so we have somewhere to put rating preds
        out = np.zeros(self.n_items)
        for item_to_rate in range(self.n_items):
            relevant_items = np.intersect1d(self.neighborhoods[item_to_rate],
                                            items_rated_by_this_user, # perfume column indices, not perfume id
                                            assume_unique=True) # return a 1d array with rated perfumes of this user
            out[item_to_rate] = np.sum(self.ratings_pivot.loc[user_id].iloc[relevant_items].reshape(1, -1) * \
                self.item_sim_mat[item_to_rate, relevant_items]) / \
                np.sum(self.item_sim_mat[item_to_rate, relevant_items])
        if report_run_time:
            print("Execution time: %f seconds" % (time()-start_time))
        cleaned_out = np.nan_to_num(out)
        return cleaned_out

    def pred_all_users(self, report_run_time=False):
        '''
        Repeated calls of pred_one_user, are combined into a single matrix.
        Return value is matrix of users (rows) items (columns) and predicted
        ratings (values).

        Optional argument to specify whether or not timing should be provided
        on this operation.
        '''
        start_time = time()
        all_ratings = [
            self.pred_one_user(user_id) for user_id in self.ratings_contents['user_id'].nunique()]
        if report_run_time:
            print("Execution time: %f seconds" % (time()-start_time))
        return np.array(all_ratings)

    def top_n_recs(self, user_id, n):
        '''
        Take user_id argument and number argument.

        Return that number of items with the highest predicted ratings, after
        removing items that user has already rated.
        '''
        pred_ratings = self.pred_one_user(user_id)
        item_index_sorted_by_pred_rating = list(np.argsort(pred_ratings))
        items_rated_by_this_user = self.ratings_pivot.loc[user_id].nonzero()[0]
        unrated_items_by_pred_rating = [item for item in item_index_sorted_by_pred_rating
                                        if item not in items_rated_by_this_user]
        rec_items = []
        for i in unrated_items_by_pred_rating[-n:]:
            rec_items.append(self.ratings_pivot.T.reset_index()['perfume_id'][i])
        return rec_items


def get_ratings_data():
    mongo_user_name, mongo_pwd = sys.argv[1], sys.argv[2]
    client = MongoClient("mongodb://{}:{}@35.164.86.3:27017/fragrance".format(mongo_user_name, mongo_pwd))
    db = client.fragrance
    collection = db.ratings_trial2
    utility_matrix = pd.DataFrame(list(collection.find({}, {'_id': 0}))) # not including _id column
    util = mm.prepare_util_mat(utility_matrix)
    ratings_contents = mm.remove_user(util)
    ratings_pivot = pd.pivot_table(ratings_contents, values='user_rating', index='user_id', columns='perfume_id', fill_value=0)
    ratings_as_mat = sparse.csr_matrix(ratings_pivot.values)
    return ratings_contents, ratings_as_mat


if __name__ == "__main__":
    ratings_contents, ratings_mat = get_ratings_data()
    my_rec_engine = ItemItemRecommender(neighborhood_size=75)
    my_rec_engine.fit(ratings_contents)
    user_1_preds = my_rec_engine.pred_one_user(user_id=33504, report_run_time=True)
    user_1_top_recs = my_rec_engine.top_n_recs(user_id=33504, n=10)
    # Show predicted ratings for user #1 on first 100 items
    print(user_1_preds[:100])
    print(my_rec_engine.top_n_recs(33504, 20))
