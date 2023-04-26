import pymongo
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
        results = await cls.db[collection].distinct(filter=filter_dict).skip(
                (page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        return results

    @classmethod
    async def exists(cls, filter_dict: dict = None, collection: str = None) -> bool:
        if not filter_dict:
            return False
        
        results = await cls.db[collection].count_documents(filter=filter_dict)
        if results > 0:
            logger.info("Record(s) exist(s).")
            return True
        
        return False
    
    @classmethod
    async def delete(cls, filter_dict:dict=None, collection:str=None) -> bool:
        try:
            _ = await cls.db[collection].delete_one(filter=filter_dict)
        except Exception as ex:
            logger.exception(f"{ex}")
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
    def find_one(cls, _id:str=None, collection:str=None):
        res = cls.db[collection].find_one({"_id":_id})
        if not res:
            return None
        return res
    
    @classmethod
    def update_one(cls, _id:str=None, data:dict=None, collection:str=None):
        if "_id" in data.keys():
            del data["_id"]

        try:
            _ = cls.db[collection].update_one(
                {"_id":_id},
                {"$set": data}
            )
        except Exception as ex:
            logger.warn(f"{ex}")
            return False

        return True

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
    def find_and_order(cls, filter_dict:dict=None, collection:str=None, sort_field:str=None, page:int=1) -> list:
        """
        Find via a query and order by a given field name.
        Useful when implementing a search.
        """
        results = cls.db[collection].find(filter_dict).sort(sort_field, pymongo.DESCENDING).skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        return list(results)


    @classmethod
    def find_distinct(cls, filter_dict: dict = None, collection: str = None, page: int = 1) -> list:
        results = cls.db[collection].distinct(filter=filter_dict).skip(
                (page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        return results
    
    @classmethod
    def count_documents(cls, filter_dict: dict = {}, collection: str = None)->int:
        return cls.db[collection].count_documents(filter=filter_dict)

    @classmethod
    def exists(cls, filter_dict: dict = None, collection: str = None) -> bool:
        if not filter_dict:
            return False
        
        if cls.db[collection].count_documents(filter=filter_dict) > 0:
            logger.info("Record(s) exist(s).")
            return True
        
        return False
    
    @classmethod
    def delete(cls, filter_dict:dict=None, collection:str=None) -> bool:
        try:
            _ = cls.db[collection].delete_one(filter=filter_dict)
        except Exception as ex:
            logger.exception(f"{ex}")
            return False
        
        return True
