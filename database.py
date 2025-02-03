from pymongo import MongoClient
from config import setting

client = MongoClient(setting.DB_URL)

db = client["ToDo"]

users_collection = db["users"]
todo_collection = db["todo"]

users_collection.create_index([("email", 1)])
todo_collection.create_index([("user_email", 1)])
def get_users_collection():
    yield users_collection

def get_todo_collection():
    yield todo_collection
