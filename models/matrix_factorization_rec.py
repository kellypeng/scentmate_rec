import graphlab as gl


def mf_model(data, num_factors=8, regularization=0.001, linear_regularization=1e-8):
    '''Fit matrix factorization model'''
    return gl.factorization_recommender.create(data,
                                            regularization=regularization,
                                            linear_regularization=linear_regularization,
                                            user_id='user_id',
                                            item_id='perfume_id',
                                            target='user_rating',
                                            num_factors=num_factors, # Number of latent factors.
                                            solver='als')


if __name__ == '__main__':
    utility_matrix = gl.SFrame.read_csv('../data/utility_matrix.csv')
    m = mf_model(utility_matrix)
    # Setup the GLC pickler
    pickler = gl._gl_pickle.GLPickler(filename = 'mf_model')
    pickler.dump(m)
    # The pickler has to be closed to make sure the files get closed.
    pickler.close()
    # When unpickle:
    # unpickler = gl_pickle.GLUnPickler
    # obj = unpickler.load()
