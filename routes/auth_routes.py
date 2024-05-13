# routes/auth_routes.py
from flask import Blueprint, redirect, url_for, session, jsonify, flash
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized
from models.user import User

# Import your GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET from config.py
from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

github_bp = make_github_blueprint(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
)
auth_bp.register_blueprint(github_bp)


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
        # Get first element because find returns a list of objects
        user = user[0]
        
        print(user.access_token)
        print(token)
    user.save()  # save to database
    # You might want to store user data in the session here for subsequent requests
    session['user_id'] = str(user._id)
    session['github_token'] = token['access_token']

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
