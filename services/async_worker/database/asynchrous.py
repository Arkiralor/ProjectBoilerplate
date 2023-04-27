import motor.motor_asyncio

from config.settings import settings
# MONGO_HOST, MONGO_NAME, MONGO_PASSWORD, MONGO_PORT, MONGO_URI, MONGO_USER

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
as_db = client[settings.MONGO_NAME]