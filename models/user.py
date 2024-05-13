# models/user.py
from models.database import get_users_collection
from pymongo.errors import DuplicateKeyError


class User:
    def __init__(
            self, username,
            email, profile_picture_url=None,
            _id=None, github_id=None, access_token=None
    ):
        self.username = username
        self.email = email
        # self.password = password
        self.profile_picture_url = profile_picture_url
        self._id = _id
        self.github_id = github_id
        self.access_token = access_token

    def __str__(self):
        return self.username

    def save(self):
        if self._id is None:
            # New user: Insert into the database
            data_dict = self.to_dict()
            data_dict.pop('_id')  
            result = get_users_collection().insert_one(data_dict)
            self._id = result.inserted_id
            print("User Created")
        else:
            # Existing user: Update the document
            result = get_users_collection().update_one(
                {"_id": self._id},
                {"$set": self.to_dict()}
            )
            if result.modified_count == 0:
                raise Exception("User not updated")
            print("User Updated")

        return self


    @staticmethod
    def find(**kwargs):
        query = kwargs
        user_documents = get_users_collection().find(query)
        # Convert to User objects
        return [User(**user) for user in user_documents]


    @staticmethod
    def delete(username):
        result = get_users_collection().delete_one({"username": username})
        return result.deleted_count > 0


    def to_dict(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "profile_picture_url": self.profile_picture_url,
            "_id": str(self._id) if self._id else None,
            "github_id": self.github_id
        }
        return user_dict
