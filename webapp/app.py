import os
from flask import Flask, render_template, request
import requests
import json
import pandas as pd
import _pickle as pickle
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
    entered = list(collection.find({'perfume_id':str(perfume_id)},  {'item_name':1,
    'brand':1, 'gender':1, 'note':1, 'tags':1, 'theme':1, '_id':0}))

    if perfume_id != None:
        recommendations = model.predict_one(str(perfume_id)) # recs is a list of perfume_id in string format
        recs = list(collection.find({'perfume_id': {'$in': recommendations}},  {'item_name':1,
            'brand':1, 'gender':1, 'note':1, 'tags':1, 'theme':1, '_id':0}))
        return render_template('table.html', perfume_id=perfume_id, entered=entered, recs=recs, fixed='some string')
    else:
        return render_template('table.html', perfume_id=perfume_id, fixed='some string')


@app.route('/getmatch',methods=['POST','GET'])
def get_delay():
    if request.method=='POST':
        result=request.form
		#Prepare the feature vector for prediction
        pkl_file = open('../models/pickled_models/perfume_df.pkl', 'rb')
        index_dict = pickle.load(pkl_file)
        new_vector = np.zeros(len(index_dict))

        try:
            new_vector[index_dict['gender_'+str(result['gender'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['note_'+str(result['note'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['tag_'+str(result['tag'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['theme_'+str(result['theme'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['DEP_HOUR_'+str(result['dep_hour'])]] = 1
        except:
            pass

        pkl_file = open('../models/pickled_models/jaccard_model.pkl', 'rb')
        jaccard_model = pickle.load(pkl_file)
        prediction = jaccard_model.predict_one(new_vector)

        return render_template('result.html',prediction=prediction)

@app.route('/try',methods=['POST','GET'])
def tryit():
    if request.method == 'POST':
        as_dict = request.form.getlist('myform')
        return render_template('try_getlist.html',as_dict=as_dict)



if __name__ == "__main__":
    perfume_df = pd.read_csv('../data/item_matrix.csv')
    perfume_df.set_index('perfume_id', inplace=True)
    with open('../models/pickled_models/jaccard_model.pkl', 'rb') as f:
        model = pickle.load(f)
    model.fit(perfume_df)


    client = MongoClient("mongodb://fragrance:fragrance@35.164.86.3:27017/fragrance")
    db = client.fragrance
    collection = db.perfume_features
    app.run(port=5000, debug=True)
