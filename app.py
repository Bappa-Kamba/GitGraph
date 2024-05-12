# app.py
from flask import Flask, g
from config import MONGO_URI
from pymongo import MongoClient
from routes.user_routes import user_bp
from routes.repository_routes import repository_bp

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
app.config['STRICT SLASHES'] = False

# Register Blueprints (Important: Register after app creation)
app.register_blueprint(user_bp)
app.register_blueprint(repository_bp)


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = MongoClient(app.config['MONGO_URI'],
                       tlsAllowInvalidCertificates=True)['GV-db']


@app.teardown_request
def teardown_request(exception):
    """Close the database connection after each request."""
    db = g.pop('db', None)
    if db is not None:
        db.client.close()


@app.route('/')
def index():
    return 'Hello, world!'


if __name__ == '__main__':
    app.run(debug=True)
