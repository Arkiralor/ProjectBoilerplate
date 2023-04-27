from django.db.models.signals import post_save, pre_save, post_delete, pre_delete

from post_app.models import Tag, Post
from post_app.utils import PostModelUtils

from post_app import logger

class PostSignalReciever:
    model = Post
    
    @classmethod
    def created(cls, sender, instance, created, *args, **kwargs):
        if created:
            _ = PostModelUtils.insert_to_mongo(post=instance)
            logger.info(f"New Post: '{instance.__str__()}' created.")

    @classmethod
    def updated(cls, sender, instance, created, *args, **kwargs):
        if not created:
            _ = PostModelUtils.update_mongo_record(post=instance)
            logger.info(f"Post: '{instance.__str__()}' updated.")

    @classmethod
    def pre_delete(cls, sender, instance, *args, **kwargs):
        _ = PostModelUtils.delete_mongo_record(post=instance)


post_save.connect(receiver=PostSignalReciever.created, sender=PostSignalReciever.model)
post_save.connect(receiver=PostSignalReciever.updated, sender=PostSignalReciever.model)
pre_delete.connect(receiver=PostSignalReciever.pre_delete, sender=PostSignalReciever.model)