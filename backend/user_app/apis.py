from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from core.boilerplate.response_template import Resp
from user_app.serializers import ShowUserSerializer
from user_app.utils import UserModelUtils, UserProfileModelUtils

from user_app import logger

class AccessTestAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request:Request, *args, **kwargs):
        resp = Resp(
            message="Access token working successfully.",
            data= {
                "user": request.user.email,
                "message": "Access token working successfully."
            },
            status_code=status.HTTP_200_OK
        )

        logger.info(resp.message)

        return resp.response()
    
    def post(self, request:Request, *args, **kwargs):
        data = request.data
        params = request.query_params
        user = request.user

        resp = Resp(
            message="Authentication successfull in POST method.",
            data={
                "body": data,
                "params": params,
                "user": ShowUserSerializer(user).data
            },
            status_code=status.HTTP_200_OK
        )

        if resp.error:
            raise resp.exception()
        
        return resp.response()


class RegisterUserAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request:Request, *args, **kwargs):
        data = request.data

        resp = UserModelUtils.create(data=data)
        if resp.error:
            raise resp.exception()
        
        return resp.response()
    
class PasswordLoginAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", "")

        resp = UserModelUtils.login_via_password(username=username, email=email, password=password)
        if resp.error:
            raise resp.exception()
        
        return resp.response()
    

class UserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request:Request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            user_id = request.user.id

        resp = UserModelUtils.get(user_id=user_id)

        if resp.error:
            raise resp.exception()
        
        return resp.response()
    
    def post(self, request:Request, page:int=1, *args, **kwargs):
        term = request.query_params.get("term", "")
        page = int(request.query_params.get("page", 1))
        logger.info(f"Term: {term}\tPage: {page}")
        resp = UserModelUtils.search(term=term, page=page)

        if resp.error:
            raise resp.exception()
        
        return resp.response()
    
    def put(self, request:Request, *args, **kwargs):
        user_id = request.user.id
        data = request.data

        resp = UserProfileModelUtils.put(user_id=user_id, data=data)

        if resp.error:
            raise resp.exception()
        
        return resp.response()
    
    def delete(self, request:Request, *args, **kwargs):
        password = request.data.get("password")
        reason = request.data.get("reason", "No reason given.")
        resp = UserModelUtils.delete(user=request.user, password=password, reason=reason)

        if resp.error:
            raise resp.exception()
        
        return resp.response()
