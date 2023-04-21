from json import loads
from os import environ

from core.settings import DEBUG, SECRET_KEY
from database.collections import DatabaseCollections
from database.methods import SynchronousMethods
from django.http import HttpRequest
from jose import jwt
from middleware_app import logger
from middleware_app.models import RequestLog
from user_app.models import User


class RequestLogger(object):
    """
    Middleware to log requests recieved by the system.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request=request, record_sql=False)
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
            logger.warn("No authorisation header.")
            return None

        try:
            if headers.get("Authorization").split(" ")[0] != token_prefix:
                logger.warn("Inavlid token prefix.")
                return None

            token = headers.get("Authorization").split(" ")[1]
            validated = jwt.decode(token=token, key=SECRET_KEY, algorithms=[environ.get('JWT_ALGORITHM'),])

            # arkiralor: Change `user_id` to whatever user identification you use in your JWT.
            return User.objects.filter(pk=validated.get("user_id")).first()
        except Exception as ex:
            logger.info(f"{ex}")
            return None

    def record_in_nosql(self, method, path, cookies, body, headers, params, user, *args, **kwargs):
        """
        Record the request in the appropriate collection in the MongoDB cluster that was set up.
        """
        no_sql_data = {
            "method": method,
            "path": path,
            "cookies": cookies,
            "body": loads(body.decode('utf8', 'strict')) if body else "",
            "headers": headers,
            "params": params,
            "user": user.email if type(user) == User else None
        }
        try:
            _ = SynchronousMethods.insert_one(
                no_sql_data, DatabaseCollections.request_logs)
        except Exception as ex:
            logger.warn(f"{ex}")

    def record_in_sql(self, method, path, cookies, body, headers, params, user, *args, **kwargs):
        """
        Record the request in the appropriate collection in the PostgreSQL table that was set up.

        NOTE: This is a lot slower but more stable than noSQL so use sparingly. Might increase response times by 2x.
        """
        try:
            _ = RequestLog.objects.create(
                method=method,
                path=path,
                cookie=cookies,
                body=body,
                body_text=body.decode('utf8', 'strict'),
                headers=headers,
                params=params,
                user=user
            )
        except Exception as ex:
            logger.exception(f"{ex}")

    def process_request(self, request: HttpRequest = None, record_sql: bool = False):
        if DEBUG and not request.path.startswith("/admin"):
            method = request.method
            path = request.path
            cookies = request.COOKIES
            body = request.body
            headers = request.headers
            params = request.content_params
            user = self.get_jwt_user(headers=headers)

            if not type(user) == User:
                user = None

            logger.info(
                f"INCOMING REQUEST: `USER: {user}\tPATH:{path}\tMETHOD: {method}`")

            self.record_in_nosql(method, path, cookies,
                                 body, headers, params, user)
            if record_sql:
                self.record_in_sql(method, path, cookies,
                                   body, headers, params, user)
