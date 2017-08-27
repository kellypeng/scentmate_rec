import os
from flask import Flask, render_template, request
import requests
import json
import pandas as pd
import cPickle as pickle
from pymongo import MongoClient
from jaccard_sim_rec import JaccardSimRec

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

# Homepage
@app.route('/')
def homepage():
    return render_template('index.html')

# predict
@app.route("/predict")
def recs(perfume_id=None):
    perfume_id = request.args.get('perfume_id')
    recommendations = model.predict_one(str(perfume_id))
    entered = list(collection.find({'perfume_id':str(perfume_id)},  {'item_name':1,
    'brand':1, 'gender':1, 'note':1, 'tags':1, 'theme':1, '_id':0}))
    preds = list(collection.find({'perfume_id':str(perfume_id)},  {'item_name':1,
    'brand':1, 'gender':1, 'note':1, 'tags':1, 'theme':1, '_id':0}))
    return render_template('table.html', entered=entered, preds=preds)



if __name__ == "__main__":
    perfume_df = pd.read_csv('/Users/kellypeng/Documents/Tech/github/Galvanize/scent_cn_rec/data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    with open('jaccard_model.pkl') as f:
        model = pickle.load(f)
    model.fit(perfume_df)


    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    collection = db.perfume_features
    app.run(port=5000, debug=True)
