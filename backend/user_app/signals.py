from django.db.models.signals import post_save, pre_save, post_delete, pre_delete

from user_app.models import User, UserProfile

from user_app import logger


class UserSignalReciever:
    model = User

    @classmethod
    def created(cls, sender, instance, created, *args, **kwargs):
        if created:
            user_profile, _ = UserProfile.objects.get_or_create(user=instance)
            logger.info(f"User: {instance.email} created.")

    @classmethod
    def updated(cls, sender, instance, created, *args, **kwargs):
        if not created:
            logger.info(f"User: '{instance.email}' updated.")


post_save.connect(receiver=UserSignalReciever.created,
                  sender=UserSignalReciever.model)
post_save.connect(receiver=UserSignalReciever.updated,
                  sender=UserSignalReciever.model)


class UserProfileSignalReciever:
    model = UserProfile

    @classmethod
    def created(cls, sender, instance, created, *args, **kwargs):
        if created:
            logger.info(f"Profile for user: '{instance.user.email}' created.")

    @classmethod
    def updated(cls, sender, instance, created, *args, **kwargs):
        if not created:
            instance.user.first_name = instance.first_name
            instance.user.last_name = instance.last_name
            instance.user.save()

            logger.info(f"Profile for user: '{instance.user.email}' updated.")


post_save.connect(receiver=UserProfileSignalReciever.created,
                  sender=UserProfileSignalReciever.model)
post_save.connect(receiver=UserProfileSignalReciever.updated,
                  sender=UserProfileSignalReciever.model)
