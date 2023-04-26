from typing import Optional, List

from django.db.models import Q, QuerySet

from rest_framework import status

from core.boilerplate.response_template import Resp
from database.collections import DatabaseCollections
from database.methods import AsynchronousMethods, SynchronousMethods
from post_app.models import Tag, Post
from post_app.serializers import TagSerializer, PostInputSerializer, PostOutputSerializer
from user_app.models import User

from post_app import logger


class TagModelUtils:

    @classmethod
    def get(cls, id:str=None, name:str=None)->Tag:
        if id and not name:
            return Tag.objects.filter(pk=id).first()
        elif not id and name:
            return Tag.objects.filter(name=name).first()
        
    @classmethod
    def search(cls, term:str=None)->List[Tag]:
        return Tag.objects.filter(
            Q(pk__icontains=term)
            | Q(name__icontains=term)
        ).order_by("name")
    
    @classmethod
    def create(cls, name:str=None)->Tag:
        tag, _ = Tag.objects.get_or_create(name=name.lower())
        return tag
    

class PostModelUtils:

    EDITABLE_FIELDS = (
        "title",
        "blurb",
        "body"
    )


    @classmethod
    def get(cls, id:str=None)->Resp:
        resp = Resp()

        obj = Post.objects.filter(pk=id).first()
        if not obj:
            resp.error = "Post Not Found"
            resp.message = f"Post with ID: '{id}' not found."
            resp.data = {"id":id}
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp
        
        serialized = PostOutputSerializer(obj).data

        resp.message = f"{obj.__repr__()} retrieved successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def create(cls, user:User=None, data:dict=None, *args, **kwargs)->Resp:
        resp = Resp()

        to_store = data.copy()

        to_store["author"] = f"{user.id}"
        if to_store.get("tags"):
            to_store["tags"] = [TagModelUtils.create(name=item).id for item in to_store.get("tags")]

        deserialized = PostInputSerializer(data=to_store)
        if not deserialized.is_valid():
            resp.error = "Invalid Data"
            resp.message = f"{deserialized.errors}"
            resp.data = data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp
        
        deserialized.save()

        _ = cls.update_tags_in_mongo(post=deserialized.instance)

        resp.message = "Post saved successfully."
        resp.data = PostOutputSerializer(deserialized.instance).data
        resp.status_code = status.HTTP_201_CREATED

        logger.info(resp.message)
        return resp
    
    @classmethod
    def update(cls, user:User=None, id:str=None, data:dict=None, *args, **kwargs)->Resp:
        resp = Resp()

        obj = Post.objects.filter(
            Q(pk=id)
            & Q(author=user)
        ).first()
        if not obj:
            resp.error = "Post Not Found"
            resp.message = f"Post with ID: '{id}' not found  or you are not the author of the post."
            resp.data = {"id":id, "user": user.username}
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp
        
        obj_data = PostInputSerializer(obj).data
        _keys = data.keys()
        for key in _keys:
            if key not in cls.EDITABLE_FIELDS:
                resp.error = "Not Allowed"
                resp.message = f"'{key}' is not allowed to be edited via this API."
                resp.data = data
                resp.status_code = status.HTTP_401_UNAUTHORIZED

                logger.warn(resp.to_text())
                return resp
            
            obj_data[key] = data.get(key)

        deserialized = PostInputSerializer(instance=obj, data=obj_data)
        if not deserialized.is_valid():
            resp.error = "Invalid Data"
            resp.message = f"{deserialized.errors}"
            resp.data = data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp
        
        deserialized.save()
        _ = cls.update_tags_in_mongo(post=deserialized.instance)

        resp.message = f"User Post '{obj.__str__()}' updated successfully."
        resp.data = PostOutputSerializer(instance=deserialized.instance).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def update_tags(cls, user:User=None, id:str=None, data:List[str]=None, *args, **kwargs)->Resp:
        resp = Resp()

        obj = Post.objects.filter(
            Q(pk=id)
            & Q(author=user)
        ).first()
        if not obj:
            resp.error = "Post Not Found"
            resp.message = f"Post with ID: '{id}' not found  or you are not the author of the post."
            resp.data = {"id":id, "user": user.username}
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp
        
        obj.tags.set([TagModelUtils.create(name=item) for item in data])
        obj.save()
        _ = cls.update_tags_in_mongo(post=obj)

        resp.message = f"Tags updated successfully for '{obj.__str__()}'."
        resp.data = PostOutputSerializer(obj).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def delete(cls, user:User=None, id:str=None)->Resp:
        resp = Resp()

        obj = Post.objects.filter(
            Q(pk=id)
            & Q(author=user)
        ).first()
        if not obj:
            resp.error = "Post Not Found"
            resp.message = f"Post with ID: '{id}' not found  or you are not the author of the post."
            resp.data = {"id":id, "user": user.username}
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp
        
        obj_data = PostOutputSerializer(obj).data
        obj.delete()

        resp.message = f"Post '{obj_data.get('id')}' deleted successfully."
        resp.data = obj_data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def insert_to_mongo(cls, post:Post)->None:
        data = {
            "_id": f"{post.id}",
            "title": post.title,
            "author": {
                "_id": f"{post.author.id}",
                "username": post.author.username,
                "email": post.author.email 
            },
            "blurb": post.blurb,
            "created": post.created,
            "updated": post.updated
        }

        try:
            _ = SynchronousMethods.insert_one(data=data, collection=DatabaseCollections.user_posts)
        except Exception as ex:
            logger.warn(f"{ex}")

        return None
    
    @classmethod
    def update_tags_in_mongo(cls, post:Post)->None:
        """
        Separate callable function to update the tags for a user post as 'ManyToMany' relation is trash in Django and the 
        `post_save` signal cannot handle the relationship.
        """
        _id = f"{post.id}"
        data = {
            "tags": [i.name for i in post.tags.all()]
        }
        try:
            _ = SynchronousMethods.update_one(_id=_id, data=data, collection=DatabaseCollections.user_posts)
        except Exception as ex:
            logger.warn(f"{ex}")

        return None
    
    @classmethod
    def update_mongo_record(cls, post:Post)->None:
        _id = f"{post.id}"

        data = {
            "title": post.title,
            "author": {
                "_id": f"{post.author.id}",
                "username": post.author.username,
                "email": post.author.email 
            },
            "blurb": post.blurb,
            "created": post.created,
            "updated": post.updated
        }

        record = SynchronousMethods.update_one(_id=_id, data=data, collection=DatabaseCollections.user_posts)
        tags = cls.update_tags_in_mongo(post=post)
        if not record or not tags:
            logger.warn(f"Could not update the MongoDB record of User Post: '{_id}' in the {DatabaseCollections.user_posts} collection.")

        return None
    
    @classmethod
    def delete_mongo_record(cls, post:Post)->None:
        _id = f"{post.id}"
        filter_dict = {
            "_id": _id
        }
        try:
            _ = SynchronousMethods.delete(filter_dict=filter_dict, collection=DatabaseCollections.user_posts)
        except Exception as ex:
            logger.warn(f"{ex}")

    @classmethod
    def search(cls, term:str, page:int=1)->Resp:
        resp = Resp()
        filter_dict = {
            "$or": [
                {
                    "_id": {"$regex": term, "$options": "i"}
                },
                {
                    "title": {"$regex": term, "$options": "i"}
                },
                {
                    "blurb": {"$regex": term, "$options": "i"}
                },
                {
                    "author._id": {"$regex": term, "$options": "i"}
                },
                {
                    "author.username": {"$regex": term, "$options": "i"}
                },
                {
                    "author.email": {"$regex": term, "$options": "i"}
                },
                {
                    "tags": {
                        "$in": [term.strip().lower()]
                    }
                }
            ]
        }

        results = SynchronousMethods.find_and_order(filter_dict=filter_dict, collection=DatabaseCollections.user_posts, sort_field="created", page=page)
        item_count = SynchronousMethods.count_documents(filter_dict=filter_dict, collection=DatabaseCollections.user_posts)
        if not results:
            resp.error = "No Results Found"
            resp.message = f"No user posts found matching '{term}'."
            resp.data = {
                "term": term,
                "page": page
            }
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp
        
        resp.message = f"{len(results)} items retrieved"
        resp.data = {
            "page": page,
            "hits": item_count,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def get_all(cls, page:int=1)->Resp:
        resp = Resp()

        results = SynchronousMethods.find_and_order(collection=DatabaseCollections.user_posts, sort_field='created', page=page)
        total = SynchronousMethods.count_documents(collection=DatabaseCollections.user_posts)
        resp.message = "Latest posts retrieved successfully"
        resp.data = {
            "page": page,
            "total": total,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    