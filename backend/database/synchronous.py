from pymongo import MongoClient
from core.settings import MONGO_HOST, MONGO_NAME, MONGO_PASSWORD, MONGO_PORT, MONGO_URI, MONGO_USER

cluster = MongoClient(MONGO_URI)
s_db = cluster[MONGO_NAME]