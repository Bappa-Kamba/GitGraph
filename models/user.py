# models/user.py
from models.database import get_users_collection
from pymongo.errors import DuplicateKeyError


class User:
    def __init__(
            self, username,
            email, updated=False, profile_picture_url=None,
            _id=None, github_id=None, access_token=None
    ):
        self.username = username
        self.email = email
        # self.password = password
        self.profile_picture_url = profile_picture_url
        self._id = _id
        self.github_id = github_id
        self.access_token = access_token
        self.updated = updated

    def __str__(self):
        return self.username

    def save(self):
        try:
            # Check for existing user by github_id
            existing_user = get_users_collection().find_one(
                {"github_id": self.github_id})

            # If existing user is found, update the data, otherwise insert a new user
            if existing_user:
                # Update the existing user
                updated_data = self.to_dict()

                # Remove the _id field so that it won't be updated
                updated_data.pop('_id')

                result = get_users_collection().update_one(
                    {"_id": existing_user['_id']},
                    {"$set": updated_data}
                )
                if result.acknowledged:
                    if result.modified_count > 0:
                        print("User updated successfully!")
                    else:
                        print("User found, but no changes were made.")
                else:
                    print("Error: Update command not acknowledged by the server.")

            else:
                # New user: Insert into the database
                data_dict = self.to_dict()
                data_dict.pop('_id')  # Remove _id field for new users
                result = get_users_collection().insert_one(data_dict)
                self._id = result.inserted_id
                print("User Created")

        except DuplicateKeyError as e:
            # Handle duplicate key error (shouldn't happen with github_id)
            print(f"Error: Duplicate key error: {e}")
            raise

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
