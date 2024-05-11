from flask import Flask
from pymongo import MongoClient
from config import MONGO_URI

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI

# Connect to MongoDB Atlas cluster
mongo_client = MongoClient(app.config['MONGO_URI'])

# Access MongoDB database and collections
db = mongo_client.get_database('GitHub-Visualizer-Cluster')
users_collection = db.get_collection('users')
repositories_collection = db.get_collection('repositories')


@app.route('/')
def index():
    return 'Hello, world!'


if __name__ == '__main__':
    app.run(debug=True)
