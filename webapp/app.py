import os
import csv
import requests
import json
import pandas as pd
import numpy as np
import _pickle as pickle
import cn_en_dict as dt
# import graphlab as gl
from flask import Flask, render_template, request
from collections import defaultdict
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


# predict based on perfume id
@app.route("/predict")
def recs(perfume_id=None):
    perfume_id = request.args.get('perfume_id')
    # Translation from CN to English
    brand_dict = dt.brand_dict()
    note_dict = dt.note_dict()
    gender_dict = dt.gender_dict()
    theme_dict = dt.theme_dict()
    entered = list(collection.find({'perfume_id':str(perfume_id)},  {'item_name':1,
    'brand':1, 'gender':1, 'note':1, 'tags':1, 'theme':1, '_id':0}))
    for elm in entered:
        try:
            elm['brand_en'] = brand_dict[elm['brand']]
            elm['gender_en'] = gender_dict[elm['gender']]
            elm['theme_en'] = theme_dict[elm['theme']]
            elm['note_en'] = [note_dict[note] for note in elm['note']]
        except:
            pass

    if perfume_id != None:
        recommendations = model.predict_one(str(perfume_id)) # recs is a list of perfume_id in string format
        recs = list(collection.find({'perfume_id': {'$in': recommendations}},  {'item_name':1,
            'brand':1, 'gender':1, 'note':1, 'theme':1, '_id':0}))
        for rec in recs:
            try:
                rec['brand_en'] = brand_dict[rec['brand']]
                rec['gender_en'] = gender_dict[rec['gender']]
                rec['theme_en'] = theme_dict[rec['theme']]
                rec['note_en'] = [note_dict[note] for note in rec['note']]
            except:
                pass
        return render_template('table.html', perfume_id=perfume_id, entered=entered, recs=recs, fixed='some string')
    else:
        return render_template('table.html', perfume_id=perfume_id, fixed='some string')


@app.route('/signin')
def login():
	return render_template('signin.html')

# @app.route('/recommend', methods=['POST','GET'])
# def recommend(userid=None):
#     if request.method=='POST':
#         userid = request.args.get('userid')
#         model = gl.load_model('../models/pickled_models/mf_model')
#         recs = model.recommend(users=[str(userid)], k=5)
#         perfume_id = [str(i) for i in recs['perfume_id']]
#         rec_perfumes = list(collection.find({'perfume_id': {'$in': perfume_id}},
#                                             {'item_name':1, 'brand':1, 'gender':1,
#                                             'note':1, 'tags':1, 'theme':1, '_id':0}))
#         return render_template('recommend.html', rec_perfumes=rec_perfumes)


@app.route('/quiz')
def quiz():
	return render_template('quiz.html')

# predict based on user input
@app.route('/getmatch',methods=['POST','GET'])
def get_match():
    if request.method=='POST':
        result=request.form
		#Prepare the feature vector for prediction
        pkl_index = open('../models/pickled_models/perfume_df.pkl', 'rb')
        index_dict = pickle.load(pkl_index)
        new_vector = np.zeros(len(index_dict))
        new_vector[index_dict['gender_'+str('中性香')]] = 1
        features = defaultdict(list)
        for key in result.keys():
            for value in result.getlist(key):
                try:
                    features[key].append(value)
                    new_vector[index_dict[key+'_'+value]] = 1
                except:
                    pass
        prediction = model.predict_by_vector(new_vector)
        recs = list(collection.find({'perfume_id': {'$in': prediction}},  {'item_name':1,
            'brand':1, 'gender':1, 'note':1, 'theme':1, '_id':0}))
        # Translation from CN to English
        brand_dict = dt.brand_dict()
        note_dict = dt.note_dict()
        gender_dict = dt.gender_dict()
        theme_dict = dt.theme_dict()
        for rec in recs:
            try:
                rec['brand_en'] = brand_dict[rec['brand']]
                rec['gender_en'] = gender_dict[rec['gender']]
                rec['theme_en'] = theme_dict[rec['theme']]
                rec['note_en'] = [note_dict[note] for note in rec['note']]
            except:
                pass
        return render_template('result.html', features=features, prediction=prediction, recs=recs)



if __name__ == "__main__":
    perfume_df = pd.read_csv('../data/rated_item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    with open('../models/pickled_models/jaccard_model.pkl', 'rb') as f:
        model = pickle.load(f)
    model.fit(perfume_df)

    ### Connect to mongo to show recommendations
    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    collection = db.perfume_features
    app.run(port=5000, debug=True)
