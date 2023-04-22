from datetime import datetime, timezone, timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.utils import timezone

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.boilerplate.response_template import Resp
from database.collections import DatabaseCollections
from database.methods import SynchronousMethods
from database.synchronous import s_db
from user_app.models import User, UserProfile
from user_app.model_choices import UserModelChoices
from user_app.serializers import UserRegisterSerializer, ShowUserSerializer, UserProfileInputSerializer, UserProfileOutputSerializer

from user_app import logger


class JWTUtils:
    """
    Utilities for basic operation on JWT.
    """
    @classmethod
    def get_tokens_for_user(cls, user: User = None):
        refresh = RefreshToken.for_user(user)

        return {
            'refreshToken': str(refresh),
            'accessToken': str(refresh.access_token),
        }


class UserModelUtils:

    @classmethod
    def get(cls, user_id: str = None) -> Resp:
        resp = Resp()

        if not user_id:
            resp.error = "Invalid Data"
            resp.message = "Please provide a valid user ID."
            resp.data = user_id
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())

        user_obj = User.objects.filter(pk=user_id).first()
        if not user_obj:
            resp.error = "User Not Found"
            resp.message = f"User with ID: {user_id} was not found in the system."
            resp.data = user_id
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warn(resp.text())
            return resp

        serialized = ShowUserSerializer(user_obj).data

        resp.message = f"User `{user_id}` retrived successfully."
        resp.data = serialized
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def search(cls, term: str = None, page: int = 1, *args, **kwargs) -> Resp:
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
        ).select_related("user")

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
    def login_via_password(cls, username: str = None, email: str = None, password: str = None, *args, **kwargs) -> Resp:
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
    def insert_deleted_user_into_mongo(
            cls, 
            data:dict=None, 
            reason:str="Some generic reason."
        )->None:
        try:
            data["_id"] = data.get("id")
            del data["id"]

            data["reason"] = reason
            data["timestamp"] = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        
            return SynchronousMethods.insert_one(data=data, collection=DatabaseCollections.deleted_users)
        except Exception as ex:
            logger.warn(f"{ex}")
            return {}


    @classmethod
    def delete(cls, user:User=None, password:str=None, reason:str=None) -> Resp:
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
        
        # deleted = cls.insert_deleted_user_into_mongo(data=ShowUserSerializer(user).data, reason=reason)        

        user.delete()

        resp.message = f"User deleted successfully."
        # resp.data = deleted
        resp.status_code = status.HTTP_200_OK
        
        logger.info(resp.message)
        return resp


class UserProfileModelUtils:

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
    def get(cls, user_id:str=None)->UserProfile:
        return UserProfile.objects.filter(user__pk=user_id).select_related("user").first()
    
    @classmethod
    def put(cls, user_id:str=None, data:dict=None)->Resp:
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

        deserialized = UserProfileInputSerializer(instance=profile, data=db_data)

        if not deserialized.is_valid():
            resp.error = "Serializer Error"
            resp.message = f"{deserialized.errors}"
            resp.data = db_data
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())
            return resp
        
        deserialized.save()
        resp.message = "Profile updated successfully."
        resp.data = UserProfileOutputSerializer(instance=deserialized.instance).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp