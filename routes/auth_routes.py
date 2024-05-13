# routes/auth_routes.py
from flask import Blueprint, redirect, url_for, session, jsonify, flash, request, g
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized
from models.user import User
from functools import wraps
from urllib.parse import urlparse, urljoin
from bson import ObjectId

# Import your GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET from config.py
from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

github_bp = make_github_blueprint(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
)
auth_bp.register_blueprint(github_bp)


# Custom Decorator
def auth_required(func):
    """Custom decorator to check if the user is authenticated."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Check session first
        if 'user_id' not in session:
            flash("You need to log in to access this page.", "error")
            return redirect(url_for("auth.login", next=request.url))

        # If user_id is in the session, try to load g.user
        from models.user import User
        user = User.find(_id=ObjectId(session['user_id']))
        if user:
            g.user = user[0]
        else:
            flash("Invalid session. Please log in again.", "error")
            return redirect(url_for("auth.login", next=request.url))

        return func(*args, **kwargs)
    return decorated_view


# Move the user fetching/creation logic here
@oauth_authorized.connect_via(github_bp)
def github_logged_in(blueprint, token):
    """
    This function is called after the user logs in with GitHub.
    """
    # If the access token is not valid or has expired
    if not token:
        flash("Failed to log in with GitHub.", category="error")
        return False

    resp = blueprint.session.get("/user")
    print(resp)
    if not resp.ok:
        msg = "Failed to fetch user info from GitHub."
        flash(msg, category="error")
        return False

    github_info = resp.json()
    print(github_info)
    # Fetch existing user by GitHub ID from the database, or create a new User if not found
    user = User.find(github_id=github_info['id'])

    if not user:
        print("Creating a new entry in db")
        user = User(
            username=github_info['login'],
            email=github_info['email'],
            profile_picture_url=github_info['avatar_url'],
            github_id=github_info['id'],
            access_token=token['access_token']
        )
    else:
        print("Trying to get data from db")
        # Update existing user's information
        user = user[0]
        user.username = github_info["login"]
        user.email = github_info["email"]
        user.profile_picture_url = github_info["avatar_url"]

    user.access_token = token['access_token']  # Always update the access token
    user.save()
    g.user = user
    print(g.user)
    # You might want to store user data in the session here for subsequent requests
    session['user_id'] = str(user._id)
    session['github_token'] = token['access_token']

    # Get the 'next' parameter from the query string
    next_url = request.args.get('next')

    # Validate the 'next' URL to prevent open redirects
    if next_url:
        next_url = urlparse(next_url)
        if next_url.netloc != '':
            flash("Invalid redirect URL", category="error")
            return redirect(url_for("index"))
        # redirect the user to the protected page
        return redirect(urljoin(request.url_root, next_url.path))

    flash("Successfully logged in with Github", category="success")
    return False


@auth_bp.route("/login")
def login():
    print("Flask-Dance Redirect URI:", url_for("auth.github.login"))
    if not github.authorized:
        return redirect(url_for("auth.github.login"))
    else:
        return redirect(url_for('index'))


@auth_bp.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
    return jsonify({"message": "Logged out successfully"}), 200
