from typing import Optional, Set, Tuple

from django.utils.translation import gettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from database.collections import DatabaseCollections
from database.methods import SynchronousMethods
from user_app.models import User

from auth import logger

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES: Set[bytes] = {
    h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES
}


class JWTAuthentication(authentication.BaseAuthentication):
    """
    A custom authentication plugin that authenticates requests through a JSON web
    token provided in a request header.

    Also checks the user's IP address for previous login activity and rejects authentication if no login
    activity from the IP address found from the requests current IP origin.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"
    user_model = User

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def authenticate(self, request: Request) -> Optional[Tuple[User, Token]]:
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        user = self.get_user(validated_token=validated_token)
        ip_address = self.get_current_ip(request=request)

        if not self.check_user_past_ip(user=user, ip=ip_address):
            raise AuthenticationFailed(
                detail="Your IP address has changed to one from where you have never logged in before, please re-login.", code="unknown_ip_address")

        return user, validated_token

    def authenticate_header(self, request: Request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request: Request) -> bytes:
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(api_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header: bytes) -> Optional[bytes]:
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            logger.warn("Empty AUTHORIZATION header sent")
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            logger.warn("Assume the header does not contain a JSON web token")
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]

    def get_validated_token(self, raw_token: bytes) -> Token:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    def get_user(self, validated_token: Token) -> User:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(
                _("Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(
                _("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(
                _("User is inactive"), code="user_inactive")

        return user

    def get_current_ip(self, request: Request) -> str:
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        except Exception as ex:
            logger.warn(f"{ex}")
            return None

    def check_user_past_ip(self, user: User, ip: str = None) -> bool:
        filter_dict = {
            "$and": [
                {
                    "user": f"{user.id}"
                },
                {
                    "ip": ip
                }
            ]
        }
        _exists = SynchronousMethods.exists(filter_dict=filter_dict, collection=DatabaseCollections.user_ips) or SynchronousMethods.exists(
            filter_dict=filter_dict, collection=DatabaseCollections.user_white_listed_ips)
        return _exists
