# models/user.py
import bcrypt
from models.database import get_users_collection
from pymongo.errors import DuplicateKeyError


class User:
    def __init__(self, username, email, password, profile_picture_url=None, _id=None):
        self.username = username
        self.email = email
        self.password = password
        self.profile_picture_url = profile_picture_url
        self._id = _id

    def __str__(self):
        return self.username

    @staticmethod
    def create(email, username, password, profile_picture_url=None):
        # Hash the password before storing
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        try:
            new_user = {
                'username': username,
                'email': email,
                'password': hashed_password,  # Store hashed password
                'profile_picture_url': profile_picture_url
            }
            result = get_users_collection().insert_one(new_user)
            return result.inserted_id
        except DuplicateKeyError:
            # Handle duplicate key error (username or email already exists)
            return None

    @staticmethod
    def find(**kwargs):
        query = kwargs
        user_documents = get_users_collection().find(query)
        # Convert to User objects
        return [User(**user) for user in user_documents]

    # Make update an instance method
    def update(self, new_data):
        if "password" in new_data:
            # Hash the new password if it's being updated
            new_data['password'] = bcrypt.hashpw(
                new_data['password'].encode('utf-8'), bcrypt.gensalt())
        result = get_users_collection().update_one(
            # Use self.username to update the specific user instance
            {"username": self.username},
            {"$set": new_data}
        )
        return result.modified_count

    @staticmethod
    def delete(username):
        result = get_users_collection().delete_one({"username": username})
        return result.deleted_count > 0

    def authenticate(self, password):
        # Compare the provided password with the stored hashed password
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def to_dict(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "profile_picture_url": self.profile_picture_url,
            "_id": str(self._id) if self._id else None
        }
        return user_dict
