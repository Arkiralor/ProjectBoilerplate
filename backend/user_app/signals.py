from django.db.models.signals import post_save, pre_save, post_delete, pre_delete

from user_app.models import User, UserProfile, UserLoginOTP
from user_app.serializers import ShowUserSerializer
from user_app.helpers import UserModelHelpers

from user_app import logger


class UserSignalReciever:
    model = User

    @classmethod
    def created(cls, sender, instance: User, created, *args, **kwargs):
        if created:
            user_profile, _ = UserProfile.objects.get_or_create(user=instance)
            logger.info(f"User: {instance.email} created.")

    @classmethod
    def updated(cls, sender, instance: User, created, *args, **kwargs):
        if not created:
            logger.info(f"User: '{instance.email}' updated.")

    @classmethod
    def pre_delete(cls, sender, instance, *args, **kwargs):
        _ = UserModelHelpers.insert_deleted_user_into_mongo(
            data=ShowUserSerializer(instance=instance).data)


post_save.connect(receiver=UserSignalReciever.created,
                  sender=UserSignalReciever.model)
post_save.connect(receiver=UserSignalReciever.updated,
                  sender=UserSignalReciever.model)
pre_delete.connect(receiver=UserSignalReciever.pre_delete,
                   sender=UserSignalReciever.model)


class UserProfileSignalReciever:
    model = UserProfile

    @classmethod
    def created(cls, sender, instance: UserProfile, created, *args, **kwargs):
        if created:
            logger.info(f"Profile for user: '{instance.user.email}' created.")

    @classmethod
    def updated(cls, sender, instance: UserProfile, created, *args, **kwargs):
        if not created:
            instance.user.first_name = instance.first_name
            instance.user.last_name = instance.last_name
            instance.user.save()

            logger.info(f"Profile for user: '{instance.user.email}' updated.")


post_save.connect(receiver=UserProfileSignalReciever.created,
                  sender=UserProfileSignalReciever.model)
post_save.connect(receiver=UserProfileSignalReciever.updated,
                  sender=UserProfileSignalReciever.model)


class UserLoginOTPSignalReciever:
    model = UserLoginOTP

    @classmethod
    def created(cls, sender, instance: UserLoginOTP, created, *args, **kwargs):
        if created:
            logger.info(
                f"Login OTP for user: '{instance.user.email}' created.")

    @classmethod
    def deleted(cls, sender, instance: UserLoginOTP, *args, **kwargs):
        logger.info(f"Login OTP for user: '{instance.user.email}' deleted.")


post_save.connect(receiver=UserLoginOTPSignalReciever.created,
                  sender=UserLoginOTPSignalReciever.model)
post_delete.connect(receiver=UserLoginOTPSignalReciever.deleted,
                    sender=UserLoginOTPSignalReciever.model)
