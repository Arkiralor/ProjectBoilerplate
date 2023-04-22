from core.settings import MAX_ITEMS_PER_PAGE
from database.asynchrous import as_db
from database.synchronous import s_db



class AsynchronousMethods:
    db = as_db

    @classmethod
    async def insert_one(cls, data:dict=None, collection:str=None)->dict:
        inserted = await cls.db[collection].insert_one(data)
        new = await cls.db[collection].find_one(
            {
                "_id": inserted.inserted_id
            }
        )

        return new
    
    @classmethod
    async def find(cls, filter_dict:dict=None, collection:str=None, page:int=1)->dict:
        if not filter_dict:
            results = await cls.db[collection].find().skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        else:
            results = await cls.db[collection].find(filter_dict).skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)

        return list(results)
    

class SynchronousMethods:
    db = s_db

    @classmethod
    def insert_one(cls, data:dict=None, collection:str=None)->dict:
        inserted = cls.db[collection].insert_one(data)
        new = cls.db[collection].find_one(
            {
                "_id": inserted.inserted_id
            }
        )

        return new
    
    @classmethod
    def find(cls, filter_dict:dict=None, collection:str=None, page:int=1)->dict:
        if not filter_dict:
            results = cls.db[collection].find().skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)
        else:
            results = cls.db[collection].find(filter_dict).skip((page-1)*MAX_ITEMS_PER_PAGE).limit(MAX_ITEMS_PER_PAGE)

        return list(results)