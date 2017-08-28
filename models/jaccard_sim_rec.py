import numpy as np
import pandas as pd
import pickle
import model_main as mm
from scipy.spatial.distance import pdist
from sklearn.metrics import pairwise_distances


class JaccardSimRec(object):

    def __init__(self, n_rec):
        self.n_rec = n_rec

    def fit(self, perfume_df):
        self.perfume_df = perfume_df
        self.perfume_matrix = perfume_df.values
        self.n_perfumes = perfume_df.values.shape[0]
        self.n_features = perfume_df.values.shape[1]

    def predict_one(self, perfume_id):
        '''
        Accept perfume id as arg.
        Return the most similar perfumes of this perfume.

        Given two vectors, u and v, the Jaccard distance is the proportion
        of those elements u[i] and v[i] that disagree.
        '''
        perfume_vec = self.perfume_df.loc[int(perfume_id)].values
        jaccard_distances = pairwise_distances(perfume_vec, self.perfume_matrix, metric='jaccard')
        rec_index = np.argsort(jaccard_distances)[0]
        recommendations = []
        i = 0
        while i <= self.n_rec:
            rec = str(self.perfume_df.index[rec_index[i]])
            if rec != perfume_id:
                recommendations.append(rec)
            i += 1
        return recommendations



if __name__ == '__main__':
    # perfume_df = pd.read_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/item_matrix.csv')
    # perfume_df.set_index('perfume_id', inplace=True)
    # perfume_df = mm.prepare_item_mat() # this takes too long, thus I've stored to a local csv file
    perfume_df = pd.read_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    jd = JaccardSimRec(n_rec=5)
    jd.fit(perfume_df)
    # with open('jaccard_model.pkl', 'wb') as f:
    #     pickle.dump(jd, f)
