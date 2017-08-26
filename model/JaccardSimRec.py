import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from sklearn.metrics import pairwise_distances


class JaccardSimilarityRec(object):

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
    perfume_df = pd.read_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    # perfume_df = mm.prepare_item_mat() # this takes too long, thus I've stored to a local csv file
    jd = JaccardSimilarityRec(n_rec=5)
    jd.fit(perfume_df)
    terre = jd.predict_one('449262') # Hermes Terre. return: ['495532', '360042', '802147', '424304', '210387']
    frederic_malle_carnal_flower = jd.predict_one('342108') # ['979263', '523117', '781391', '341881', '841241']
