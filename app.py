from flask import Flask, g, session, redirect, flash, url_for, jsonify, request
from functools import wraps
from config import MONGO_URI, SECRET_KEY
from pymongo import MongoClient
from routes.user_routes import user_bp
from routes.repository_routes import repository_bp
from routes.auth_routes import auth_bp, auth_required
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


@app.teardown_request
def teardown_request(exception):
    """Close the database connection after each request."""
    db = g.pop('db', None)
    if db is not None:
        db.client.close()


@app.route('/')
@auth_required
def index():
    return 'Hello, world!'


@app.route('/mock_login')
def mock_login():
    from models.user import User
    # Replace with your actual test user data (from GitHub)
    mock_user = User.find(username='Senior_Man')

    if not mock_user:
        flash("Mock user not found in the database. Please create the user first.", "error")
        return jsonify({"user_not_found" : "Check database for test_user"})

    # Get the first element of mock_user if it exists
    session['user_id'] = str(mock_user[0]._id)
    session['github_token'] = 'mock_token1122e'

    print(session['user_id'])
    print(session['github_token'])
    print(session)

    flash("Mocked GitHub login successful", category="success")
    return redirect(url_for("index"))


if __name__ == '__main__':
    # Generate a self-signed certificate (adjust paths as needed)
    cert, key = make_ssl_devcert('adhoc', host='localhost')
    context = (cert, key)
    app.run(ssl_context=context, debug=True)
