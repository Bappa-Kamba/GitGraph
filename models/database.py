from flask import g
from pymongo import MongoClient
from config import MONGO_URI


def get_db():
    if 'db' not in g:
        g.db = MongoClient(MONGO_URI,
                           tlsAllowInvalidCertificates=True)['GV-db']

    return g.db


def get_users_collection():
    db = get_db()
    return db['users']


def get_repositories_collection():
    db = get_db()
    return db['repositories']
