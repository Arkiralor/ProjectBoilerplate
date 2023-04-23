from uuid import uuid4

from core.settings import MAX_ITEMS_PER_PAGE
from database.asynchrous import as_db
from database.synchronous import s_db

from database import logger


class AsynchronousMethods:
    """
    Methods to query the declared MongoDB cluster asynchronously.
    """
    db = as_db

    @classmethod
    async def insert_one(cls, data: dict = None, collection: str = None) -> dict:
        if not data.get("_id"):
            data["_id"] = f"{uuid4()}".replace("-", "").upper()

        if await cls.find(filter_dict={"_id": data.get("_id")}, collection=collection):
            logger.warn(f"_id already exits.")
            return {}

        inserted = await cls.db[collection].insert_one(data)
        new = await cls.db[collection].find_one(
            {
                "_id": inserted.inserted_id
            }
        )

        return new

    @classmethod
    async def find(cls, filter_dict: dict = None, collection: str = None, page: int = 1) -> list:
        if not filter_dict:
            results = await cls.db[collection].find().skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        else:
            results = await cls.db[collection].find(filter_dict).skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)

        return list(results)

    @classmethod
    async def find_distinct(cls, filter_dict: dict = None, collection: str = None, page: int = 1) -> list:
        results = await cls.find(filter_dict=filter_dict, collection=collection, page=page)
        return list(set(results))

    @classmethod
    async def exists(cls, filter_dict: dict = None, collection: str = None) -> bool:
        if not filter_dict:
            return False

        result = await cls.db[collection].count_documents(filter=filter_dict)
        logger.info(f"Count: {result}")
        if not result > 0:
            return False

        return True


class SynchronousMethods:
    """
    Methods to query the declared MongoDB cluster synchronously.
    """
    db = s_db

    @classmethod
    def insert_one(cls, data: dict = None, collection: str = None) -> dict:
        if not data.get("_id"):
            data["_id"] = f"{uuid4()}".replace("-", "").upper()

        if cls.find(filter_dict={"_id": data.get("_id")}, collection=collection):
            logger.warn(f"_id already exits.")
            return {}

        inserted = cls.db[collection].insert_one(data)
        new = cls.db[collection].find_one(
            {
                "_id": inserted.inserted_id
            }
        )

        return new

    @classmethod
    def find(cls, filter_dict: dict = None, collection: str = None, page: int = 1) -> list:
        if not filter_dict:
            results = cls.db[collection].find().skip(
                (page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        else:
            results = cls.db[collection].find(filter_dict).skip(
                (page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)

        return list(results)

    @classmethod
    def find_distinct(cls, filter_dict: dict = None, collection: str = None, page: int = 1) -> list:
        results = cls.find(filter_dict=filter_dict,
                           collection=collection, page=page)
        return list(set(results))

    @classmethod
    def exists(cls, filter_dict: dict = None, collection: str = None) -> bool:
        if not filter_dict:
            return False

        result = cls.db[collection].count_documents(filter=filter_dict)
        logger.info(f"Count: {result}")
        if not result > 0:
            return False

        return True
