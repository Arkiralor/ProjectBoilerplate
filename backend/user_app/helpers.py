from datetime import datetime, timezone, timedelta
from typing import List, Dict
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone

from rest_framework import status

from communications_app.email_utils import DjangoEmailUtils
from core.boilerplate.response_template import Resp
from core.settings import MAC_HEADER
from database.collections import DatabaseCollections
from database.methods import SynchronousMethods
from database.synchronous import s_db
from user_app.models import User, UserProfile, UserLoginOTP, UserPasswordResetToken, UserToken
from user_app.model_choices import UserModelChoices
from user_app.serializers import UserRegisterSerializer, ShowUserSerializer, UserProfileInputSerializer, UserProfileOutputSerializer,\
    UserLoginOTPInputSerializer, UserLoginOTPOutputSerializer, UserPasswordResetTokenInputSerializer, UserPasswordResetTokenOutputSerializer, \
    UserTokenInputSerializer, UserTokenOutputSerializer, UserTokenUsageInputSerializer, UserTokenUsageOutputSerializer
from user_app.utils import JWTUtils, LoginOTPUtils, UserTokenUtils

from user_app import logger


class UserModelHelpers:
    """
    Utility methods for operations on user model objects.
    """

    @classmethod
    def get(cls, user_id: str = None) -> Resp:
        """
        Get basic information about a user.
        """
        resp = Resp()

        if not user_id:
            resp.error = "Invalid Data"
            resp.message = "Please provide a valid user ID."
            resp.data = user_id
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())

        user_obj = User.objects.filter(pk=user_id).first()
        if not user_obj:
            resp.error = "User Not Found"
            resp.message = f"User with ID: {user_id} was not found in the system."
            resp.data = user_id
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp

        serialized = ShowUserSerializer(user_obj).data

        resp.message = f"User `{user_id}` retrived successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def search(cls, term: str = None, page: int = 1, *args, **kwargs) -> Resp:
        """
        Search for users via string argument.
        """
        resp = Resp()
        if not term:
            resp.error = "Invalid Data"
            resp.message = "Please provide a valid search term."
            resp.data = term
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())
            return resp

        users = UserProfile.objects.filter(
            Q(pk__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(user__pk__icontains=term)
            | Q(user__username__icontains=term)
            | Q(user__email__icontains=term)
        ).select_related("user").order_by("user__username")

        if not users:
            resp.error = "No Users Found"
            resp.message = "No users found matching the search query."
            resp.data = term
            resp.status_code = status.HTTP_200_OK

            logger.info(resp.text())
            return resp

        paginated = Paginator(users, settings.MAX_ITEMS_PER_PAGE)
        users = paginated.get_page(page)

        serialized = UserProfileOutputSerializer(users, many=True).data

        resp.message = "Search results obtained."
        resp.data = {
            "page": page,
            "results": serialized
        }

        logger.info(resp.message)
        return resp

    @classmethod
    def check_if_user_exists(cls, username: str = None, phone: str = None, email: str = None, *args, **kwargs) -> bool:
        """
        Check if a user with the given parameters is registered in the system.
            username
            email
        """
        return User.objects.filter(
            Q(username__iexact=username)
            | Q(email__iexact=email)
        ).exists()

    @classmethod
    def create(cls, data: dict = None, user_type: str = UserModelChoices.user, *args, **kwargs) -> Resp:
        """
        Register a new user in the system.
        """
        resp = Resp()

        if cls.check_if_user_exists(username=data.get('username'), email=data.get('email')):
            resp.error = "User Exists."
            resp.data = data
            resp.message = f"A user with the given credentials (username | email) already exists."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        _keys = data.keys()

        if "user_type" in _keys:
            del data['user_type']
        if "is_superuser" in _keys:
            del data['is_superuser']
        if 'is_staff' in _keys:
            del data['is_staff']

        data['user_type'] = user_type
        if user_type == UserModelChoices.admin:
            data['is_superuser'] = True

        data['password'] = make_password(data.get('password'))

        deserialized = UserRegisterSerializer(data=data)
        is_valid = deserialized.is_valid()

        if not is_valid:
            resp.data = deserialized.data
            resp.error = "Invalid Data"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        deserialized.save()
        serialized = ShowUserSerializer(deserialized.instance)

        resp.data = serialized.data
        resp.message = f"User {serialized.instance.email} registered succesfully."
        resp.status_code = status.HTTP_201_CREATED

        return resp

    @classmethod
    def block_user(cls, user: User = None, blocked_until: int = settings.OTP_ATTEMPT_TIMEOUT, *args, **kwargs) -> Resp:
        """
        Block a single user for a pre-defined amount of time.
        Most commonly to be used when there is an excessive amount of unsuccessfull login attempts.
        """
        resp = Resp()

        if not user:
            resp.error = "User Instance Required."
            resp.message = "User Instance Required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)
            return resp

        user.unsuccessful_login_attempts = 0
        user.blocked_until = timezone.now() + timezone.timedelta(minutes=blocked_until)
        user.save()

        resp.error = "User Blocked"
        resp.message = f"Too many unsuccessfull login attempts. User {user.email} is blocked for {blocked_until} minutes, until {user.blocked_until}."
        resp.data = {
            "user": user.id,
            "blockedUntil": user.blocked_until.strftime("YYYY-MM-dd HH:mm:ss")
        }
        resp.status_code = status.HTTP_401_UNAUTHORIZED
        return resp

    @classmethod
    def get_ip_address(cls, request: HttpRequest = None):
        """
        Get the IP address from a request.
        To be used when logging a user's IP address when logging in.
        """
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        except Exception as ex:
            logger.warn(f"{ex}")
            return ""

    @classmethod
    def log_login_ip(cls, user: str = None, request: HttpRequest = None) -> None:
        """
        Log a user's IP address when successfully logging in.
        """
        ip = cls.get_ip_address(request=request)
        if ip:
            try:
                data = {
                    "_id": f"{uuid4()}".replace("-", "").upper(),
                    "user": user,
                    "ip": ip,
                    "userAgent": request.headers.get("User-Agent", "").split("/")[0],
                    "timestampUtc": datetime.utcnow()
                }

                _ = SynchronousMethods.insert_one(
                    data=data, collection=DatabaseCollections.user_ips)
            except Exception as ex:
                logger.warn(f"{ex}")

    @classmethod
    def login_via_password(cls, username: str = None, email: str = None, password: str = None, *args, **kwargs) -> Resp:
        """
        Log in a user via their password.
        """
        resp = Resp()
        user: User = None

        if not username and not email:
            resp.error = "Invalid Request"
            resp.message = "Either username or email are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        if username and not email:
            user = User.objects.filter(
                username__iexact=username, is_active=True).first()
        elif email and not username:
            user = User.objects.filter(
                email__iexact=email, is_active=True).first()
        else:
            resp.error = "Invalid Request"
            resp.message = "Send either the USERNAME or the EMAIL, not both."
            resp.status_code = status.HTTP_300_MULTIPLE_CHOICES
            return resp

        if not user:
            resp.error = "User not found."
            resp.message = "User not found for the given credentials, please check again."
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp

        if user.blocked_until and user.blocked_until > timezone.now():
            resp.error = "Login Blocked"
            resp.message = f"The user is blocked from logging in until {user.blocked_until}."
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

        if not check_password(password=password, encoded=user.password):
            user.unsuccessful_login_attempts += 1
            user.save()

            if user.unsuccessful_login_attempts > settings.OTP_ATTEMPT_LIMIT:
                resp = cls.block_user(user=user)
                return resp

            resp.error = "Invalid Credentials"
            resp.message = "The entered password is incorrect."
            resp.data = {
                "username": username,
                "email": email,
                "password": password,
                "attemptsLeft": settings.OTP_ATTEMPT_LIMIT - user.unsuccessful_login_attempts
            }
            resp.status_code = status.HTTP_403_FORBIDDEN
            return resp

        if user.unsuccessful_login_attempts != 0:
            user.unsuccessful_login_attempts = 0
            user.save()
        if user.blocked_until:
            user.blocked_until = None
            user.save()

        user.last_login = timezone.now()
        user.save()

        tokens = JWTUtils.get_tokens_for_user(user=user)

        resp.message = f"User {user.email} logged in successfully."
        resp.data = {
            "user": user.id,
            "tokens": tokens,
            "login": timezone.now()
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(
            f"User {user.email} logged in at {resp.data.get('login')} via password.")

        return resp

    @classmethod
    def otp_login_init(cls, username: str = None, email: str = None, *args, **kwargs) -> Resp:
        resp = Resp()

        if username and email:
            resp.error = "Invalid Request"
            resp.message = "Send either the USERNAME or the EMAIL, not both."
            resp.status_code = status.HTTP_300_MULTIPLE_CHOICES
            return resp

        if not username and not email:
            resp.error = "Invalid Request"
            resp.message = "Either username or email are required."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        if username:
            user = User.objects.filter(username__iexact=username).first()
        else:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            resp.error = "User not found."
            resp.message = "User not found for the given credentials, please check again."
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp

        if user.blocked_until and user.blocked_until > timezone.now():
            resp.error = "Login Blocked"
            resp.message = f"The user is blocked from logging in until {user.blocked_until}."
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

        otp = LoginOTPUtils.generate_numeric_otp()
        otp_object = LoginOTPUtils.assign_otp_to_user(user=user, otp=otp)
        if not otp_object:
            resp.error = "Internal Error"
            resp.message = "Internal server error; check logs."
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return resp

        if settings.ENV_TYPE == "dev":
            resp.message = f"Sending OTP in `Response` as this is a development environment."
            resp.data = {
                "otp": otp,
                "id": f"{otp_object.id}",
                "user": ShowUserSerializer(otp_object.user).data,
                "otp_expires_at": otp_object.otp_expires_at
            }
            resp.status_code = status.HTTP_200_OK

            logger.info(resp.message)
            return resp

        email_resp = DjangoEmailUtils.send_otp_email(
            user=user, otp=otp)
        if email_resp.error:
            return email_resp

        resp.message = f"OTP sent to {user.email}."
        resp.data = UserLoginOTPOutputSerializer(otp_object).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def login_via_otp(cls, otp: str = None, otp_id: str = None) -> Resp:
        resp = Resp()
        otp_object = UserLoginOTP.objects.filter(pk=otp_id).first()
        if not otp_object:
            resp.error = "Invalid OTP"
            resp.message = "The OTP entered is invalid."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        user = otp_object.user

        if user.blocked_until and user.blocked_until > timezone.now():
            resp.error = "Login Blocked"
            resp.message = f"The user is blocked from logging in until {user.blocked_until}."
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

        if otp_object.otp_expires_at < timezone.now():
            resp.error = "OTP Expired"
            resp.message = "The OTP entered is expired; please request a new one."
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        if not check_password(password=otp, encoded=otp_object.otp):
            user.unsuccessful_login_attempts += 1
            user.save()
            if user.unsuccessful_login_attempts > settings.OTP_ATTEMPT_LIMIT:
                resp = cls.block_user(user=user)
                return resp

            resp.error = "Invalid OTP"
            resp.message = "The OTP entered is invalid."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        if user.unsuccessful_login_attempts != 0:
            user.unsuccessful_login_attempts = 0
            user.save()

        if user.blocked_until:
            user.blocked_until = None
            user.save()

        user.last_login = timezone.now()
        user.save()

        tokens = JWTUtils.get_tokens_for_user(user=user)

        resp.message = f"User {user.email} logged in successfully."
        resp.data = {
            "user": ShowUserSerializer(user).data,
            "tokens": tokens,
            "login": user.last_login
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def insert_deleted_user_into_mongo(
        cls,
        data: dict = None,
        reason: str = "Some generic reason."
    ) -> None:
        """
        Keep a record of any deleted users in the MongoDB cluster.
        """
        try:
            data["_id"] = data.get("id", f'{uuid4()}')
            del data["id"]

            data["reason"] = reason
            data["timestamp"] = timezone.now().strftime(
                '%Y-%m-%dT%H:%M:%S.%f%z')

            return SynchronousMethods.insert_one(data=data, collection=DatabaseCollections.deleted_users)
        except Exception as ex:
            logger.warn(f"{ex}")
            return {}

    @classmethod
    def delete(cls, user: User = None, password: str = None, reason: str = None) -> Resp:
        """
        Utility method for a user to delete their account.
        """
        resp = Resp()

        if not user or not password:
            resp.error = "Missing Data"
            resp.message = "Both user and password are required."
            resp.data = {
                "user": user.email,
                "password": password
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)
            return resp

        if not check_password(password, user.password):
            resp.error = "Incorrect Password"
            resp.message = resp.error
            resp.data = {
                "user": user.email,
                "password": password
            }
            resp.status_code = status.HTTP_401_UNAUTHORIZED

            logger.warn(resp.message)
            return resp

        user.delete()

        resp.message = f"User deleted successfully."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def get_whitelisted_ips(cls, user: User = None, page: int = 1) -> Resp:
        resp = Resp()

        if not user:
            resp.error = "Invalid Argument(s)"
            resp.message = "'User' is a mandatory argument."
            resp.data = {
                "user": user
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())
            return resp

        filter_dict = {
            "user": f"{user.id}"
        }

        results = SynchronousMethods.find(
            filter_dict=filter_dict, collection=DatabaseCollections.user_white_listed_ips, page=page)

        resp.message = f"White-listed IP addresses for '{user.email}' retrieved successfully."
        resp.data = {
            "page": page,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def add_white_list_ips(cls, user: User = None, password: str = None, ips: List[str] = []) -> Resp:
        resp = Resp()

        if not user or not check_password(password=password, encoded=user.password):
            resp.error = "Invalid Credentials"
            resp.message = "The entered password is incorrect."
            resp.data = {
                "user": user.email if user else None,
                "password": password,
            }
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warn(resp.text())
            return resp

        for ip in ips:
            try:
                data = {
                    "user": f"{user.id}",
                    "ip": ip
                }

                if SynchronousMethods.find(filter_dict=data, collection=DatabaseCollections.user_white_listed_ips):
                    logger.warn(
                        "This IP is already whitelisted for this user.")
                else:
                    _ = SynchronousMethods.insert_one(
                        data=data, collection=DatabaseCollections.user_white_listed_ips)
            except Exception as ex:
                resp.error = "Error in MongoDB Insertion"
                resp.message = f"{ex}"
                resp.data = data
                resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

                logger.exception(resp.text())
                return resp

        results = cls.get_whitelisted_ips(user=user)
        if results.error:
            return resp

        resp.message = f"White-listed IP for {user.email} updated successfully."
        resp.data = results.data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def delete_whitelisted_ip(cls, user: User = None, ip: str = None, _id: str = None) -> Resp:
        resp = Resp()

        if not user:
            resp.error = "Argument 'user' invalid"
            resp.message = "USER is a mandatory argument."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())

        filter_dict = {}
        filter_dict["user"] = f"{user.id}"

        if _id and not ip:
            filter_dict["_id"] = _id
        elif not _id and ip:
            filter_dict["ip"] = ip
        elif _id and ip:
            logger.info(
                f"Contructing complicated filter hash table for MongoDB query for {user.username} as both: '_id' and 'ip' were provided")
            filter_dict = {
                "$and": [
                    {"user": f"{user.id}"},
                    {
                        "$or": [
                            {"_id": _id},
                            {"ip": ip}
                        ]
                    }
                ]
            }
            logger.info(f"Filter Hash Table:\t{filter_dict}")
        else:
            resp.error = "Invalid Data"
            resp.message = "Invalid arguments sent."
            resp.data = {
                "ip": ip,
                "_id": _id
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        if not SynchronousMethods.find(filter_dict=filter_dict, collection=DatabaseCollections.user_white_listed_ips):
            resp.error = "Document Not Found"
            resp.message = f"No document found with attributes: {filter_dict} in collection '{DatabaseCollections.user_white_listed_ips}'."
            resp.data = filter_dict
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp

        check = SynchronousMethods.delete(
            filter_dict=filter_dict, collection=DatabaseCollections.user_white_listed_ips)
        if not check:
            resp.error = "Internal Error"
            resp.message = f"Internal server error; check logs."
            resp.data = filter_dict
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            logger.warn(resp.to_text())
            return resp

        resp.message = f"Whitelisted IP address {ip if ip else _id} deleted for {user.email}."
        resp.data = cls.get_whitelisted_ips(user=user).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def log_login_mac(self, user: str = None, request: HttpRequest = None) -> None:
        mac = request.headers.get(MAC_HEADER)
        if mac:
            try:
                data = {
                    "_id": f"{uuid4()}".replace("-", "").upper(),
                    "user": user,
                    "mac": mac,
                    "timestampUtc": datetime.utcnow()
                }
                _ = SynchronousMethods.insert_one(
                    data=data, collection=DatabaseCollections.user_mac_addresses)
            except Exception as ex:
                logger.warn(f"{ex}")


class UserProfileModelHelpers:

    EDITABLE_FIELDS = (
        "first_name",
        "middle_name",
        "last_name",
        "age",
        "regnal_number",
        "date_of_birth",
        "gender"
    )

    @classmethod
    def get(cls, user_id: str = None) -> UserProfile:
        return UserProfile.objects.filter(user__pk=user_id).select_related("user").first()

    @classmethod
    def put(cls, user_id: str = None, data: dict = None) -> Resp:
        resp = Resp()

        if not user_id or not data:
            resp.error = "No Data"
            resp.message = f"Both User ID and update data required."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)
            return resp

        profile = cls.get(user_id=user_id)

        db_data = UserProfileInputSerializer(profile).data

        _keys = data.keys()

        for key in _keys:
            if key not in cls.EDITABLE_FIELDS:
                resp.error = "Disallowed Field"
                resp.message = f"{key} is not allowed to be edited via this API."
                resp.data = data
                resp.status_code = status.HTTP_401_UNAUTHORIZED

                logger.warn(resp.text())
                return resp

            db_data[key] = data.get(key)

        deserialized = UserProfileInputSerializer(
            instance=profile, data=db_data)

        if not deserialized.is_valid():
            resp.error = "Serializer Error"
            resp.message = f"{deserialized.errors}"
            resp.data = db_data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())
            return resp

        deserialized.save()
        resp.message = "Profile updated successfully."
        resp.data = UserProfileOutputSerializer(
            instance=deserialized.instance).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp


class UserTokenHelpers:

    BLANK: str = ""

    @classmethod
    def get(cls, user:User)->Resp:
        resp = Resp()

        if not user:
            resp.error = "Invalid Data"
            resp.message = "User ID is required."
            resp.data = user
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        user_tokens = UserToken.objects.filter(user=user)

        serialized = UserTokenOutputSerializer(user_tokens, many=True).data

        resp.message = f"Tokens for user `{user.email}` retrived successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def create(cls, user_id: str = None, alias: str = None, expires_at: str = None) -> Resp:
        resp = Resp()

        if not user_id or user_id == cls.BLANK:
            resp.error = "Invalid Data"
            resp.message = "User ID is required."
            resp.data = user_id
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        user = User.objects.filter(pk=user_id).first()
        if not user:
            resp.error = "User Not Found"
            resp.message = f"User with ID: {user_id} was not found in the system."
            resp.data = user_id
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp

        token = UserTokenUtils.create_permanent_token(usr=user)
        if not token:
            resp.error = "Internal Error"
            resp.message = "Internal server error; check logs."
            resp.data = user_id
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            logger.warn(resp.to_text())
            return resp
        user_part, token_part = UserTokenUtils.split_parts(token=token)

        data = {
            "user": f"{user.id}",
            "token": make_password(token_part),
            "alias": alias,
            "expires_at": expires_at
        }

        deserialized = UserTokenInputSerializer(data=data)
        if not deserialized.is_valid():
            resp.error = "Invalid Data"
            resp.message = f"{deserialized.errors}"
            resp.data = data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        deserialized.save()

        resp.message = "Please save the token as you will not be able to recover the token once this view ends."
        resp.data = {
            "user": f"{user.id}",
            "token": token,
            "alias": deserialized.data.get("alias"),
            "expires_at": deserialized.data.get("expires_at")
        }
        resp.status_code = status.HTTP_201_CREATED

        logger.info(resp.message)
        return resp

    @classmethod
    def destroy(cls, user: User, alias: str, _id: str) -> Resp:
        resp = Resp()

        if not user:
            resp.error = "Invalid Data"
            resp.message = "User ID is required."
            resp.data = user
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        if alias and alias != cls.BLANK:
            user_token = UserToken.objects.filter(
                Q(user=user)
                & Q(alias=alias)
            ).first()
        elif _id and _id != cls.BLANK:
            user_token = UserToken.objects.filter(
                Q(user=user)
                & Q(pk=_id)
            ).first()
        else:
            resp.error = "Invalid Data"
            resp.message = "Either alias or _id is required."
            resp.data = {
                "user": f"{user.id}",
                "alias": alias,
                "_id": _id
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp

        deserialized = UserTokenOutputSerializer(user_token)

        if not user_token:
            resp.error = "Token Not Found"
            resp.message = f"Token with ID: {_id} was not found in the system."
            resp.data = {
                "user": f"{user.id}",
                "alias": alias,
                "_id": _id
            }
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.to_text())
            return resp

        user_token.delete()

        resp.message = "Token deleted successfully."
        resp.data = deserialized.data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp


class UserTokenUsageHelpers:

    @classmethod
    def create(cls, data: Dict[str, str]) -> Resp:
        deserialized = UserTokenUsageInputSerializer(data=data)
        if not deserialized.is_valid():
            _msg: str = f"{deserialized.errors}"
            raise Exception(_msg)
        
        deserialized.save()
        return