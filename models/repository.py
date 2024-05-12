# models/repository.py

from models.database import get_repositories_collection
from pymongo.errors import DuplicateKeyError


class Repository:
    def __init__(self, name, owner, description, url, _id=None):
        self.name = name
        self.owner = owner
        self.description = description
        self.url = url
        self._id = _id

    def __str__(self):
        return f'{self.owner}/{self.name} - {self.description}'

    @classmethod
    def create(cls, name, owner, description, url):
        try:
            new_repo = {
                "name": name,
                "owner": owner,
                "description": description,
                "url": url
            }
            result = get_repositories_collection().insert_one(new_repo)
            # Return Repository object
            return cls(_id=result.inserted_id, **new_repo)
        except DuplicateKeyError:
            return None

    @staticmethod
    def find(**kwargs):
        query = kwargs
        repository_documents = get_repositories_collection().find(query)
        return [Repository(**repo) for repo in repository_documents]

    def update(self, new_data):
        result = get_repositories_collection().update_one(
            {"_id": self._id},
            {"$set": new_data}
        )
        return result.modified_count > 0

    def delete(self):
        result = get_repositories_collection().delete_one({"_id": self._id})
        return result.deleted_count > 0

    def to_dict(self):
        repo_dict = {
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "url": self.url,
            "_id": str(self._id) if self._id else None
        }
        return repo_dict
