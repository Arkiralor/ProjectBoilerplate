from os import environ
from jose import jwt

from database.collections import DatabaseCollections
from database.methods import SynchronousMethods
from django.http import HttpRequest, HttpResponseForbidden

from core.settings import SECRET_KEY
from user_app.models import User

from middleware_app import logger


class IpAddressChecker(object):
    """
    Middleware to check if the user is accessing from an IP address they have previously logged-in from.
    This is to prevent session-token theft from being viable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resp = self.process_request(request=request)
        if resp:
            return resp
        return self.get_response(request)

    def get_jwt_user(
        self,
        headers: dict = None,
        token_prefix: str = "Bearer"
    ):
        """
        Method to get the user from the header of the request, if authentication is handled
        by a JWT.

        Change `token_prefix` to whatever prefix your system uses.
        """

        if not headers.get("Authorization"):
            logger.warn("No authorization header.")
            return None

        try:
            if headers.get("Authorization").split(" ")[0] != token_prefix:
                logger.warn("Inavlid token prefix.")
                return None

            token = headers.get("Authorization").split(" ")[1]
            validated = jwt.decode(token=token, key=SECRET_KEY, algorithms=[
                                   environ.get('JWT_ALGORITHM'),])
            return User.objects.filter(pk=validated.get("user_id")).first()
        except Exception as ex:
            logger.info(f"{ex}")
            return None

    def get_client_ip(self, request: HttpRequest):
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

    def check_previous_ip(self, user_id: str = None, ip: str = None):
        filter_dict = {
            "$and": [
                {
                    "user": user_id
                },
                {
                    "ip": ip
                }
            ]
        }
        _exists = SynchronousMethods.exists(
            filter_dict=filter_dict, collection=DatabaseCollections.user_ips)
        return _exists

    def process_request(self, request: HttpRequest):
        headers = headers = request.headers
        user = request.user
        ip = self.get_client_ip(request=request)

        if not user or not type(user) == User:
            user = self.get_jwt_user(headers=headers)

        if user and not (user.is_superuser or user.is_staff) and not self.check_previous_ip(user_id=f"{user.id}", ip=ip):
            return HttpResponseForbidden(
                content="Your IP address has changed to one from where you have never logged in before, please re-login."
            )
