import pandas as pd
import numpy as np
import graphlab
import matplotlib.pyplot as plt

def rmse(theta, thetahat):
    ''' Compute Root-mean-squared-error '''
    return np.sqrt(np.mean((theta - thetahat) ** 2))

def get_data(util):
    sf = graphlab.SFrame(util)
    return sf



