# ScentMate
###### Capstone Project &bull; g45 &bull; Kelly Peng &bull; 09/2017

---

![homepage](/img/homepage.png)

**Check out the final product** on: 34.212.206.24



&nbsp;
## Motivation

Fragrance is not only about scent, it tells your personality, or the impression you want to leave on people. People with different personality types will like different scents. So this is what I did a few months ago, when I was looking for my "perfect match":

![story](/img/story.png)

Then I thought, as a data scientist, I should be able to answer the question using my data science knowledge. Help people find their signature perfumes, that is what ScentMate is all about.

**ScentMate, find your perfect match.**

&nbsp;
## Recommendation Systems

Think about Pandora, Netflix, Youtube, Amazon...One common characteristic of them is that they personalize what each user receives based on user preferences, and this is what recommendation systems are about. Recommendation systems have become increasingly more popular in recent years as a way for companies to provide better service and increase profit. In a broad sense, recommendation systems predict the level of interest a user has in a new item.

Different architectures for a recommender system:
1. **Popularity Based Recommender** Make the same recommendation to every user, based on the popularity of an item.
2. **Content-Based Recommender** focus on properties of items. Similarity of items is determined by measuring the similarity in their properties. Different types of content-based systems:
   1. Classification/Regression
   2. Item content similarity (Jaccard similarity, cosine similarity)
   3. Word2Vec
3. **Collaborative Filtering Recommender** focus on the relationship between users and items. Similarity of items is determined by the similarity of the ratings of those items by the users who have rated both items.
   1. Item-item similarity
   2. User-user similarity
   3. Matrix Factorization

For this project, I will implement different approaches, targeting at different consumer groups. For cold start problem (new users and intermediate users without much rating history), I will use content based models, for users with rating history, I will implement item-item similarity collaborative filtering model and matrix factorization model.

![user_groups](/img/user_groups.png)



&nbsp;
## Workflow

![workflow](/img/workflow.png)



&nbsp;
## Data

The data I scraped from website are two tables. One table is perfume data, which includes features such as:

* Number of Perfumes: 20k
* Brand: 1,824
* Gender: 3
* Note: 653
* Theme: 30

Another table is user rating data:

* Number of Ratings: 40k
* Perfume ID
* User ID
* Rating Score: Range 2 - 10
* User Comment

&nbsp;
## Models

1. **Model 1**: Content-Based Recommender

In order to gather more meaningful features for each perfume, such as people's feeling about each perfume, I applied NMF and LDA to user comments for topic modeling. After comparing the topics from both methods, I chose 12 topics generated by LDA, and then combined LDA keywords together with other perfume features, built perfume matrix, then built content-based similarity model based on Jaccard similarity.

2. **Model 2**: Collaborative Filtering Recommender

||Base Model|Item-item Similarity|Funk SVD (UV decomposition)|
------|------|------|-----|
Methodology|Predict mean for everything|Recommend based on the most similar items found by user ratings|Decompose utility matrix into two matrices with 14 latent factors, added regularization
Performance on Test Set|RMSE: 2.20|RMSE: 7.32|RMSE: 1.95|
Reason||Utility matrix too sparse lead to little information going into each prediction|Should perform better if more data available

&nbsp;
## How did I do train-test split and cross-validation

Whenever someone says “I built a recommender”, the first question came to my mind is: “How did you validate your recommender’s performance?” Because it is the most challenging part of any recommendation systems. In my project, for content-based recommender, since it is unsupervised and recommended completely based on the perfume features, I validated it by letting my classmates try and see the result. The recommendations in general were good, especially the "Find Similar" function on the home page, but the biggest drawback is that perfume price data is not available, a customer who loves Chanel perfumes will not probably go to a mass market brand even though they have similar ingredients. However for the "Take a Quiz" function on the home page, if a user only selected a few features, the result will be off because the model is building a vector based on all the features a user selected and calculate Jaccard distance between the user vector and every perfume.

For the collaborative filtering recommender, the first cross-validation method I tried was leave-one-out cross validation, but it took me 18 hours to finish one cycle, which is too computationally expensive, thus I switched to manual K-fold validation. First, I manually removed users with less than 3 ratings, treat them as part of cold start problem and let them use the content-based recommender instead. Then, for users with 3 or more ratings, I made sure every user exists in my training set, validation set, and test set. Therefore I can use the user’s rating in the training set to fit the model, predict the rating of the user’s other ratings in the validation set, and tune the model based on RMSE on the validation set. And finally, I used the user’s ratings in the test set to evaluate the final model.

&nbsp;
## Limitations
1. No price data, which has a big impact on content-based recommender's performance
2. Some fragrance products have no reviews at all, the reason can be they are too old/new/unpopular, these perfumes are not included in dataset

&nbsp;
## Tools Used
- Data processing and EDA: Numpy, Pandas, Matplotlib, Plotly, Seaborn
- Machine learning and stats: Numpy, Pandas, Graphlab, Scikit-learn, Scipy
- Web Scaping: BeautifulSoup, urllib2
- Data Storage: pymongo, MongoDB
- Cloud Computing: AWS S3, EC2
- Web App: Flask, Bootstrap, HTML, CSS


&nbsp;
