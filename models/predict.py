import pandas as pd
import cPickle as pickle
from time import time
from jaccard_sim_rec import JaccardSimRec












if __name__ == "__main__":
    start_time = time()
    perfume_df = pd.read_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    with open('jaccard_model.pkl') as f:
        model = pickle.load(f)
    model.fit(perfume_df)
    print ("Loading Model Run time: %s seconds" % (time() - start_time))

    # recommendations = model.predict_one('623126')
    # terre = jd.predict_one('449262') # Hermes Terre. return: ['495532', '360042', '802147', '424304', '210387']
    # frederic_malle_carnal_flower = jd.predict_one('342108') # ['979263', '523117', '781391', '341881', '841241']
