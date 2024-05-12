# models/database.py
from flask import g
from pymongo import MongoClient
from config import MONGO_URI


def get_db():
    if 'db' not in g:
        # You can pass the MONGO_URI directly to MongoClient
        g.db = MongoClient(MONGO_URI,
                           tlsAllowInvalidCertificates=True)['GV-db']

    return g.db


def get_users_collection():
    return get_db().get_collection('users')


def get_repositories_collection():
    return get_db().get_collection('repositories')
