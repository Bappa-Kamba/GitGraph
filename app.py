from flask import Flask
from pymongo import MongoClient
from config import MONGO_URI
from routes.user_routes import user_bp
from routes.repository_routes import repository_bp  # Add this import


app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
app.register_blueprint(user_bp)
app.register_blueprint(repository_bp)  # Add this line


@app.route('/')
def index():
    return 'Hello, world!'


if __name__ == '__main__':
    app.run(debug=True)
