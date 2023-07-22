from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from auth.authentication import TokenAuthentication
from core.boilerplate.response_template import Resp
from user_app.serializers import ShowUserSerializer
from user_app.helpers import UserModelHelpers, UserProfileModelHelpers, UserTokenHelpers

from user_app import logger


class AccessTestAPI(APIView):
    authentication_classes = (JWTAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        resp = Resp(
            message="Access token working successfully.",
            data={
                "user": request.user.email,
                "message": "Access token working successfully."
            },
            status_code=status.HTTP_200_OK
        )

        logger.info(resp.message)

        return resp.to_response()

    def post(self, request: Request, *args, **kwargs):
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

        return resp.to_response()


class RegisterUserAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        data = request.data

        resp = UserModelHelpers.create(data=data)

        _ = UserModelHelpers.log_login_ip(
            user=f"{resp.data.get('id', '')}", request=request)
        return resp.to_response()


class PasswordLoginAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", "")

        resp = UserModelHelpers.login_via_password(
            username=username, email=email, password=password)

        if not resp.error:
            _ = UserModelHelpers.log_login_ip(
                user=f"{resp.data.get('user', '')}", request=request)
            _ = UserModelHelpers.log_login_mac(
                user=f"{resp.data.get('user', '')}", request=request)
        return resp.to_response()


class OTPLoginInitAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        resp = UserModelHelpers.otp_login_init(username=username, email=email)
        return resp.to_response()


class OTPLoginConfirmAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        otp = request.data.get("otp", "")
        otp_id = request.data.get("otp_id", "")
        resp = UserModelHelpers.login_via_otp(otp=otp, otp_id=otp_id)
        if not resp.error:
            _ = UserModelHelpers.log_login_ip(
                user=f"{resp.data.get('user').get('id', '')}", request=request)
            _ = UserModelHelpers.log_login_mac(
                user=f"{resp.data.get('user').get('id', '')}", request=request)
        return resp.to_response()


class UserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            user_id = request.user.id

        resp = UserModelHelpers.get(user_id=user_id)

        return resp.to_response()

    def post(self, request: Request, page: int = 1, *args, **kwargs):
        term = request.query_params.get("term", "")
        page = int(request.query_params.get("page", 1))

        resp = UserModelHelpers.search(term=term, page=page)

        return resp.to_response()

    def put(self, request: Request, *args, **kwargs):
        user_id = request.user.id
        data = request.data

        resp = UserProfileModelHelpers.put(user_id=user_id, data=data)

        return resp.to_response()

    def delete(self, request: Request, *args, **kwargs):
        password = request.data.get("password")
        reason = request.data.get("reason", "No reason given.")
        resp = UserModelHelpers.delete(
            user=request.user, password=password, reason=reason)

        if resp.error:
            return resp.to_exception()

        return resp.to_response()


class WhiteListIpAddressAPI(APIView):
    """
    API for a user to set/get Whitelisted IP addresses.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        """
        Get all IP addresses whitelisted for user.
        """
        page = int(request.query_params.get("page", 1))
        resp = UserModelHelpers.get_whitelisted_ips(
            user=request.user, page=page)

        return resp.to_response()

    def post(self, request: Request, *args, **kwargs):
        """
        Add IP addresses to whitelist for user.
        """
        password = request.data.get("password", None)
        ip_addresses = request.data.get("ip_addresses", [])

        if not type(ip_addresses) == list and not type(ip_addresses) == set:
            ip_addresses = [ip_addresses]

        resp = UserModelHelpers.add_white_list_ips(
            user=request.user, password=password, ips=ip_addresses)

        return resp.to_response()

    def delete(self, request: Request, *args, **kwargs):
        """
        Delete a single whitelisted IP address for a user.
        """
        _id = request.data.get("id")
        ip = request.data.get("ip")

        resp = UserModelHelpers.delete_whitelisted_ip(
            user=request.user, ip=ip, _id=_id)

        return resp.to_response()


class UserTokenAPI(APIView):

    authentication_classes = (JWTAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        resp = UserTokenHelpers.get(user=request.user)

        return resp.to_response()

    def post(self, request: Request, *args, **kwargs):
        user_id = f"{request.user.id}"
        alias = request.data.get("alias", None)
        expires_at = request.data.get("expires_at", None)
        resp = UserTokenHelpers.create(
            user_id=user_id,
            alias=alias,
            expires_at=expires_at
        )

        return resp.to_response()

    def delete(self, request: Request, *args, **kwargs):
        _id = request.data.get("id", None)
        alias = request.data.get("alias", None)
        resp = UserTokenHelpers.destroy(
            user=request.user,
            _id=_id,
            alias=alias
        )

        return resp.to_response()
