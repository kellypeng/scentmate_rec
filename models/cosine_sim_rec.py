import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity


class CosineSimilarityRec(object):

    def __init__(self, n_rec):
        self.n_rec = n_rec

    def fit(self, perfume_matrix):
        self.perfume_df = perfume_df
        self.perfume_matrix = perfume_df.values
        self.n_perfumes = perfume_df.values.shape[0]
        self.n_features = perfume_df.values.shape[1]

    def predict_one(self, perfume_id):
        """
        Accept perfume id as arg. Return the most similar perfumes of this perfume
        """
        perfume_vec = self.perfume_df.loc[int(perfume_id)].values
        cs = cosine_similarity(perfume_vec, self.perfume_matrix)
        rec_index = np.argsort(cs)[0][::-1]
        recommendations = []
        i = 0
        while i <= self.n_rec:
            rec = str(self.perfume_df.index[rec_index[i]])
            if rec != perfume_id:
                recommendations.append(rec)
            i += 1
        return recommendations



if __name__ == '__main__':
    perfume_df = pd.read_csv('../data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    cs = CosineSimilarityRec(n_rec=5)
    cs.fit(perfume_df)
    terre = cs.predict_one('449262') # Hermes Terre. return: ['495532', '360042', '802147', '424304', '210387'] same result as Jaccard
    frederic_malle_carnal_flower = cs.predict_one('342108') # ['979263', '781391', '523117', '279103', '868232'] differnt with Jaccard
