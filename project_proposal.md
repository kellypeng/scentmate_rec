# ScentMate
###### Capstone Project Final Proposal &bull; g45 &bull; Yuwei(Kelly) Peng &bull; 08/13/2017

---

### Motivation

Fragrance is not only about scent, it tells your personality, or the impression you want to leave on people. People with different personality types will like different scents. In addition to personality, mood, environment, season all affects people's choice of fragrances.

Among 130,000 fragrance products in the world, do you know which fragrance is your perfect match? Do you know how to pick the right fragrance for the one you care about? What's people's impression of the fragrance you like? Is that the way you want people to think about you? That's what ScentMate is all about.

ScentMate, find your perfect match.
&nbsp;
### Recommendation Systems

Think about Pandora, Netflix, Youtube, Amazon...One common characteristic of them is that they personalize what each user receives based on user preferences, and this is what recommendation systems are about. Recommendation systems have become increasingly more popular in recent years as a way for companies to provide better service and increase profit. In a broad sense, recommendation systems predict the level of interest a user has in a new item.

Different architectures for a recommender system:
1. **Popularity Based Recommender** Make the same recommendation to every user, based on the popularity of an item.
2. **Content-Based Recommender** focus on properties of items. Similarity of items is determined by measuring the similarity in their properties. Different types of content-based systems:
   1. Classification/Regression
   2. Item content similarity (Jaccard similarity, cosine similarity)
   3. Word2Vec
   4. Non-Negative Matrix Factorization (NMF)
3. **Collaborative Filtering Recommender** focus on the relationship between users and items. Similarity of items is determined by the similarity of the ratings of those items by the users who have rated both items.
   1. Item-item similarity
   2. User-user similarity
   3. Matrix Factorization

For this project, I will implement different approaches. For cold start problem, I will use content based models, for users with rating history, I will implement collaborative filtering and matrix factorization models. For each scenario, select the approach that returns the best prediction.

&nbsp;
### Data Pipeline Breakdown

The data I scraped from website can be transformed into two matrices. One matrix is completely about fragrance information, which includes these features:

 * Fragrance Name
 * Fragrance Brand
 * Fragrance Main Accords
 * Top Notes
 * Middle Notes
 * Base Notes
 * Number of Ratings

Another matrix is composed of both user and fragrance information, which includes these features:

   * Member ID
   * My Ratings
   * My Reviews (These involves NLP, will analyze depends on project progress)
&nbsp;

After the data for the two matrices are ready, the next step workflow will be:

- _**Step 1**:_ Split dataset into training set and test test (For matrix factorization model, use LOOCV, for collaborative filtering model, use random train test split)
- _**Step 2**:_ Use fragrance matrix only, manually label fragrance features build item content similarity recommendation systems
- _**Step 3**:_ Use user-fragrance utility matrix, build a matrix factorization model
- _**Step 4**:_ Build first version of web app for the content based model
- _**Step 5**:_ Use user-fragrance utility matrix, feed in collaborative filtering model
- _**Step 6**:_ Use fragrance matrix only, apply NMF
- _**Step 7**:_ Use fragrance matrix only, try Word2Vec
- _**Step 8**:_ Select or combine multiple models together as final model
- _**Step 9**:_ Fine-tune a web app as final product

&nbsp;
### Project Timeline
#### Week 1

_Weekend Before_:
1. Set up AWS S3 and EC2 instance
2. Scrape all data needed
3. Parse and store into usable format

_Day 1_:
1. Clean data, outliers, missing values, etc
2. EDA
3. Label fragrance features for similarity model
4. Search for papers about recommendation systems

_Day 3_:
1. Continue fragrance features for similarity model
2. Build base models using GraphLab
3. Cross validate

_Day 4_:
1. Code algorithms not using GraphLab
   + Collaborative-Filtering
   + Matrix Factorization
2. Cross-validation

_Day 5_:
1. Continue working on coding the algorithms
2. Tune model if necessary
3. Finish first iteration, close the first loop

_Weekend_:
Build a simple version web app

#### Week 2

1. Make more iterations. Tune model if necessary
2. If time allows, do nlp for user review text data, to extract key words in user review, to analyze relationship between fragrance notes v.s. user feeling
3. Try Word2Vec for content based model
3. Fine tune web app

&nbsp;
### Anticipated Problems
1. No price data, which has a big impact on recommendations' accuracy
2. Some fragrance products have no reviews at all, the reason can be they are too old/new/unpopular, need to consider how to deal with them.
3. For each feature, there can be multiple values under it. For example, top note/middle note/bottom note usually consists of 3-4 ingredients, need to think about how to translate multiple ingredients under each feature into model.

&nbsp;
### Tools Consider Using
- Data processing and EDA: Pandas, Numpy, Matplotlib, Seaborn
- Baseline recommender models: Graphlab
- Machine learning and stats: Scikit-learn, Scipy, PySpark
- Web Scaping: BeautifulSoup, urllib2
- Data Storage: pymongo, MongoDB
- AWS: S3, EC2
&nbsp;
### Data
1. **Fragrance Product**: 21,023 fragrances

2. **User Profile**: 6,478 users

3. **Rating Data**: 31,037 ratings
---
&nbsp;
