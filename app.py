from flask import Flask, g, session, request, redirect
from config import MONGO_URI, SECRET_KEY
from pymongo import MongoClient
from routes.user_routes import user_bp
from routes.repository_routes import repository_bp
from routes.auth_routes import auth_bp
from bson import ObjectId
from werkzeug.serving import make_ssl_devcert

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['STRICT SLASHES'] = False

# Register Blueprints (Important: Register after app creation)
app.register_blueprint(user_bp)
app.register_blueprint(repository_bp)
app.register_blueprint(auth_bp)


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = MongoClient(app.config['MONGO_URI'],
                       tlsAllowInvalidCertificates=True)['GV-db']
    if 'user_id' in session:
        from models.user import User
        g.user = User.find(_id=ObjectId(session['user_id']))[0]


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
    # Generate a self-signed certificate (adjust paths as needed)
    cert, key = make_ssl_devcert('adhoc', host='localhost')
    context = (cert, key)
    app.run(ssl_context=context, debug=True)
