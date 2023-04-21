from auth import logger
from django.http import HttpRequest
from rest_framework.permissions import BasePermission
from user_app.model_choices import UserModelChoices


class IsModerator(BasePermission):
    '''
    Allows access to moderators or administrators.
    '''

    def has_permission(self, request: HttpRequest, view):
        logger.info('Checking if user has Moderator access.')
        try:
            is_true = (
                (request.user.is_staff or request.user.is_superuser or request.user.user_type ==
                 UserModelChoices.moderator)
                and request.user.is_authenticated
            )
            return bool(is_true)
        except Exception as ex:
            logger.warn(f"ERROR: {ex}")
            return False
