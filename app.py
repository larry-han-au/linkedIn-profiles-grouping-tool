from flask import Flask
from flask import render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model fucntions
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80))
  link = db.Column(db.Text)
  img_link = db.Column(db.String(200))
  description = db.Column(db.Text)

  def __init__(self, name, link, img_link, description):
    self.name = name
    self.link = link
    self.img_link = img_link
    self.description = description

  def __repr__(self):
    return '<User {} {} {} {}>'.format(self.name, self.link, self.img_link ,self.description)

db.create_all()
db.session.commit()

# Clustering functions
def clean(des):
  letters_only = re.sub("[^a-zA-Z]", " ", des)
  lower_case = letters_only.lower()
  words = lower_case.split()
  words = [w for w in words if not w in stopwords.words("english")]
  return (" ".join(words))

def clustering(users):
  # users  = User.query.all()
  names = list(map(lambda x: x.name, users))
  descriptions = list(map(lambda x: x.description, users))
  clean_descritpions = list(map(lambda x: clean(x), descriptions))
  vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = 5000) 
  train_data_features = vectorizer.fit_transform(clean_descritpions)
  train_data_features = train_data_features.toarray()
  pca = PCA(n_components = 2)
  X_pca = pca.fit_transform(train_data_features)
  kmeans = KMeans(n_clusters=4, random_state=1).fit(X_pca)

  coordinates = list(map(lambda x: [round(x[0], 2), round(x[1], 2)], X_pca.tolist()))
  labels = kmeans.labels_.tolist()
  clusters = []
  for i in range(0, len(names)):
    clusters.append({"name": names[i], "x": coordinates[i][0], "y":coordinates[i][1], "label":labels[i]})
  return clusters

def profiles_clusters():
  users = User.query.all()
  res = dict()
  list = []
  clusters = clustering(users)
  for u in users:
    temp = dict()
    temp['name'] = u.name
    temp['link'] = u.link
    temp['img'] = u.img_link
    temp['des'] = u.description
    list.append(temp)

  for i in range(0, len(list)):
    list[i]['label'] = clusters[i]['label']
  res['profiles'] = list
  res['clusters'] = clusters
  return res


def writeThroughDatebase(data):
  db.drop_all()
  db.create_all()
  db.session.commit()

  count = 0
  while(count < 30):
    items = data[0]
    for item in items:
      if 'hcard' in item['pagemap']:
        if 'title' in item['pagemap']['hcard'][0]:
          name = item['title'].split(' | ')[0]
          link = item['formattedUrl']
          description = item['pagemap']['hcard'][0]['title']
          if 'photo' in item['pagemap']['hcard'][0]:
            img_link = item['pagemap']['hcard'][0]['photo']
            user = User(name, link, img_link, description)
            db.session.add(user)
            db.session.commit()
            count = count + 1
            if count == 30:
              return
    if data[1]:
      data = searchProfiles(data[2], data[1])
    else:
      return

# Router and Controller fucntions
@app.route("/")
def index():
  res = profiles_clusters()
  return render_template('index.html', data=res)

@app.route("/query", methods=["POST"])
def query():
  name = request.form['query'].strip()
  data = searchProfiles(name, 1)
  writeThroughDatebase(data)
  return redirect(url_for('index'))

def searchProfiles(query, index):
  splitted_list = query.split()
  formatted_query = "+".join(splitted_list)
  api_key = "AIzaSyDPmT0Arh7zNjGIugvXU2Fgv-jYHhJmAPY"
  cx = "015718152841429576125:fm39xw_dpui"
  base_url = "https://www.googleapis.com/customsearch/v1?"
  constructed_url = base_url + "key=" + api_key + "&q=" + formatted_query + "&cx=" + cx
  if index:
    constructed_url = constructed_url + "&start=" + str(index)
  r = requests.get(constructed_url)
  json = r.json()
  if 'queries' in json and 'nextPage' in json['queries']:
    return (json['items'], json['queries']['nextPage'][0]['startIndex'], query)
  else:
    return (json['items'], None, query)


if __name__ == "__main__":
  app.debug = True
  app.run()