import motor.motor_asyncio

from core.settings import MONGO_HOST, MONGO_NAME, MONGO_PASSWORD, MONGO_PORT, MONGO_URI, MONGO_USER

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
as_db = client[MONGO_NAME]