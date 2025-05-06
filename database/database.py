from pymongo import MongoClient
from config.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_triggers():
    return list(db.triggers.find({}))

def store_user(user_id, username):
    db.users.update_one({"id": user_id}, {"$set": {"name": username}}, upsert=True)
