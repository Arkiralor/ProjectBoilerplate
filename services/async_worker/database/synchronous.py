from pymongo import MongoClient
from config.settings import settings 
# MONGO_HOST, MONGO_NAME, MONGO_PASSWORD, MONGO_PORT, MONGO_URI, MONGO_USER

cluster = MongoClient(settings.MONGO_URI)
s_db = cluster[settings.MONGO_NAME]