from os import environ

from django.http import HttpRequest

from core.settings import DEBUG
from middleware_app.models import RequestLog
from user_app.models import User

from jose import jwt

from middleware_app import logger


class RequestLogger(object):
    """
    Middleware to log requests recieved by the system.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request=request)
        return self.get_response(request)
    
    def get_jwt_user(
            self, 
            headers:dict=None,
            token_prefix:str="Bearer"
        ):
        
        try:
            if headers.get("Authorization").split(" ")[0] != token_prefix:
                logger.warn("Inavlid token prefix.")
                return None
            
            token = headers.get("Authorization").split(" ")[1]
            validated = jwt.decode(token=token, key=environ.get('SECRET_KEY'), algorithms=[environ.get('JWT_ALGORITHM'),])
            return User.objects.filter(pk=validated.get("user_id")).first()
        except Exception as ex:
            logger.info(f"{ex}")
            return None

    def process_request(self, request: HttpRequest = None):
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
                f"INCOMING REQUEST: `USER: {user}, PATH:{path}, METHOD: {method}`")
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
