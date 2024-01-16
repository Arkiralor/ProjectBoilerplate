from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.db.models import Q, F
from django.http import HttpRequest
from django.utils import timezone

from rest_framework.authentication import BaseAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions


from user_app.models import User, UserToken, UserTokenUsage
from user_app.helpers import UserTokenUsageHelpers
from user_app.utils import UserTokenUtils

from auth import logger


def get_authorization_header(request: HttpRequest):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class TokenAuthentication(BaseAuthentication):
    """
    Encrypted token-based authentication
    """

    KEYWORD = 'Token'
    MODEL = UserToken

    def get_model(self):
        if self.MODEL is not None:
            return self.MODEL
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate(self, request: HttpRequest):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.KEYWORD.lower().encode():
            return None
        if len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            raw_token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            logger.error(msg)
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(raw_token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        user_part, token_part = UserTokenUtils.split_parts(token)
        if not user_part or not token_part:
            logger.error('Incorrect token format.')
            raise exceptions.AuthenticationFailed('Incorrect token format.')

        user_id = UserTokenUtils.get_user_id(user_part=user_part)
        if not user_id:
            logger.error('User ID not found.')
            raise exceptions.AuthenticationFailed('User ID not found.')

        NOW: datetime = timezone.now()
        user_tokens = model.objects.filter(
            Q(user__id=user_id)
            & Q(expires_at__gte=NOW)
        ).select_related('user')
        if not user_tokens:
            logger.error('Token object not found or is expired.')
            raise exceptions.AuthenticationFailed('Token object not found or is expired.')

        for token_obj in user_tokens:
            if check_password(token_part, token_obj.token):
                UserTokenUsageHelpers.create(data = {"token": f"{token_obj.id}", "created": NOW})
                return token_obj.user, token_obj

        raise exceptions.AuthenticationFailed(
            'Token does not exist or is expired.')
