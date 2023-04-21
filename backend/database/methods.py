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